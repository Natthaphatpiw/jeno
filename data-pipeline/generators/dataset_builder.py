import os
import json
import random
from typing import List, Dict, Optional, Tuple
import jsonlines
from tqdm import tqdm

from config.settings import settings
from models.schemas import TrainingExample, DatasetStats, ProcessingStats
from prompts.prompt import JenosizePromptGenerator
from processors.content_extractor import ContentExtractor
from utils.logger import get_logger
from utils.helpers import save_json, load_json, ensure_dir_exists

logger = get_logger(__name__)

class DatasetBuilder:
    """Build training and validation datasets for fine-tuning"""
    
    def __init__(self):
        self.prompt_generator = JenosizePromptGenerator()
        self.content_extractor = ContentExtractor()
        ensure_dir_exists(settings.OUTPUT_DIR)
        
    def build_datasets(self, processed_articles: List[Dict]) -> DatasetStats:
        """Build complete training and validation datasets"""
        logger.info(f"Building datasets from {len(processed_articles)} processed articles")
        
        # Filter and prepare articles for training
        training_ready_articles = self._prepare_articles_for_training(processed_articles)
        logger.info(f"Found {len(training_ready_articles)} articles suitable for training")
        
        if not training_ready_articles:
            logger.error("No articles suitable for training found")
            return DatasetStats()
        
        # Generate training examples
        training_examples = self._generate_training_examples(training_ready_articles)
        logger.info(f"Generated {len(training_examples)} training examples")
        
        # Split into train and validation sets
        train_examples, validation_examples = self._split_dataset(training_examples)
        
        # Save datasets
        self._save_jsonl_dataset(train_examples, 'train.jsonl')
        self._save_jsonl_dataset(validation_examples, 'validation.jsonl')
        
        # Generate statistics
        stats = self._calculate_dataset_stats(training_examples, train_examples, validation_examples)
        
        # Save metadata
        self._save_dataset_metadata(stats, training_ready_articles)
        
        logger.info(f"Dataset building completed: {stats.train_examples} train, {stats.validation_examples} validation examples")
        return stats
    
    def _prepare_articles_for_training(self, articles: List[Dict]) -> List[Dict]:
        """Prepare and filter articles for training data generation"""
        training_ready = []
        
        logger.info("Preparing articles for training...")
        
        for article in tqdm(articles, desc="Processing articles"):
            try:
                # Check if article is already processed and training ready
                if article.get('training_ready'):
                    training_ready.append(article)
                    logger.debug(f"Article ready for training: {article.get('metadata', {}).get('url', 'unknown')}")
                else:
                    # Fallback: Extract training-suitable content if not already processed
                    training_content = self.content_extractor.extract_training_content(article)
                    
                    if training_content and training_content.get('training_ready'):
                        training_ready.append(training_content)
                    else:
                        logger.debug(f"Article not suitable for training: {article.get('metadata', {}).get('url', 'unknown')}")
            
            except Exception as e:
                logger.warning(f"Error preparing article for training: {e}")
                continue
        
        return training_ready
    
    def _generate_training_examples(self, articles: List[Dict]) -> List[TrainingExample]:
        """Generate training examples from articles"""
        examples = []
        
        logger.info("Generating training examples...")
        
        for article in tqdm(articles, desc="Generating examples"):
            try:
                # Generate multiple examples per article with variations
                article_examples = self._create_examples_from_article(article)
                examples.extend(article_examples)
                
            except Exception as e:
                logger.error(f"Error generating examples from article {article['metadata']['url']}: {e}")
                continue
        
        return examples
    
    def _create_examples_from_article(self, article: Dict) -> List[TrainingExample]:
        """Create multiple training examples from a single article"""
        examples = []
        
        try:
            content = article['content']
            metadata = article['metadata']
            structured = article['structured_content']
            
            # Generate base example
            base_example = self.prompt_generator.create_training_example(
                content, metadata, structured
            )
            
            examples.append(TrainingExample(
                system_prompt=base_example['messages'][0]['content'],
                user_input=base_example['messages'][1]['content'],
                assistant_response=base_example['messages'][2]['content'],
                metadata={
                    'source_url': metadata['url'],
                    'category': metadata['category'],
                    'complexity': metadata.get('complexity_level', 'intermediate'),
                    'theme': metadata.get('primary_theme', 'business'),
                    'example_type': 'base'
                }
            ))
            
            # Generate example with source content simulation
            if len(content) > 1000:  # Only for substantial content
                source_simulation = content[:800] + "..."  # Simulate source content
                source_example = self.prompt_generator.create_training_example(
                    content, metadata, structured, source_simulation
                )
                
                examples.append(TrainingExample(
                    system_prompt=source_example['messages'][0]['content'],
                    user_input=source_example['messages'][1]['content'],
                    assistant_response=source_example['messages'][2]['content'],
                    metadata={
                        'source_url': metadata['url'],
                        'category': metadata['category'],
                        'complexity': metadata.get('complexity_level', 'intermediate'),
                        'theme': metadata.get('primary_theme', 'business'),
                        'example_type': 'with_source'
                    }
                ))
            
            # Generate example with custom instructions
            custom_instructions = self._generate_custom_instructions(metadata, structured)
            if custom_instructions:
                # Update user prompt to include custom instructions
                custom_example = self.prompt_generator.create_training_example(
                    content, metadata, structured
                )
                
                # Modify user prompt to include custom instructions
                original_user = custom_example['messages'][1]['content']
                custom_user = original_user.replace(
                    "Return your response as a JSON object",
                    f"CUSTOM USER INSTRUCTIONS: {custom_instructions}\n\nReturn your response as a JSON object"
                )
                
                examples.append(TrainingExample(
                    system_prompt=custom_example['messages'][0]['content'],
                    user_input=custom_user,
                    assistant_response=custom_example['messages'][2]['content'],
                    metadata={
                        'source_url': metadata['url'],
                        'category': metadata['category'],
                        'complexity': metadata.get('complexity_level', 'intermediate'),
                        'theme': metadata.get('primary_theme', 'business'),
                        'example_type': 'with_custom_instructions'
                    }
                ))
            
        except Exception as e:
            logger.error(f"Error creating examples from article: {e}")
        
        return examples
    
    def _generate_custom_instructions(self, metadata: Dict, structured: Dict) -> Optional[str]:
        """Generate realistic custom instructions based on article characteristics"""
        
        category = metadata.get('category', '')
        theme = metadata.get('primary_theme', '')
        complexity = metadata.get('complexity_level', 'intermediate')
        
        # Template custom instructions based on content characteristics
        instructions_templates = [
            "Focus on practical implementation steps that business leaders can follow immediately",
            "Include more statistical data and concrete examples from real companies",
            "Emphasize the ROI and business impact of the recommendations",
            "Structure the article with clear action items and next steps",
            "Include potential challenges and how to overcome them",
            "Focus on small to medium-sized enterprises rather than large corporations",
            "Add more case studies showing successful implementation",
            "Include a timeline for implementation and expected results"
        ]
        
        # Category-specific instructions
        category_instructions = {
            'futurist': "Focus on emerging trends and their potential business impact in the next 2-3 years",
            'transformation-and-technology': "Emphasize step-by-step digital transformation strategies",
            'real-time-marketing': "Include specific marketing tactics and campaign examples",
            'understand-people-and-consumer': "Focus on consumer psychology and behavioral insights",
            'utility-for-our-world': "Emphasize sustainability metrics and ESG considerations",
            'experience-the-new-world': "Include user journey mapping and experience design principles"
        }
        
        # Complexity-based instructions
        complexity_instructions = {
            'basic': "Keep explanations simple and accessible to non-technical readers",
            'advanced': "Include technical details and sophisticated analytical frameworks",
            'intermediate': "Balance technical depth with practical accessibility"
        }
        
        # Combine instructions
        instructions = []
        
        # Add random general instruction
        instructions.append(random.choice(instructions_templates))
        
        # Add category-specific instruction
        if category in category_instructions:
            instructions.append(category_instructions[category])
        
        # Add complexity-based instruction
        if complexity in complexity_instructions:
            instructions.append(complexity_instructions[complexity])
        
        return '; '.join(instructions) if instructions else None
    
    def _split_dataset(self, examples: List[TrainingExample]) -> Tuple[List[TrainingExample], List[TrainingExample]]:
        """Split examples into training and validation sets"""
        
        # Shuffle examples to ensure random distribution
        shuffled_examples = examples.copy()
        random.shuffle(shuffled_examples)
        
        # Calculate split point
        train_size = int(len(shuffled_examples) * settings.TRAIN_SPLIT_RATIO)
        
        train_examples = shuffled_examples[:train_size]
        validation_examples = shuffled_examples[train_size:]
        
        logger.info(f"Dataset split: {len(train_examples)} training, {len(validation_examples)} validation")
        
        return train_examples, validation_examples
    
    def _save_jsonl_dataset(self, examples: List[TrainingExample], filename: str) -> None:
        """Save dataset in JSONL format for OpenAI fine-tuning"""
        
        filepath = os.path.join(settings.OUTPUT_DIR, filename)
        
        logger.info(f"Saving {len(examples)} examples to {filepath}")
        
        with jsonlines.open(filepath, 'w') as writer:
            for example in examples:
                writer.write(example.to_openai_format())
        
        logger.info(f"Saved {filename} successfully")
    
    def _calculate_dataset_stats(self, 
                                all_examples: List[TrainingExample],
                                train_examples: List[TrainingExample], 
                                validation_examples: List[TrainingExample]) -> DatasetStats:
        """Calculate comprehensive dataset statistics"""
        
        stats = DatasetStats()
        
        # Basic counts
        stats.total_examples = len(all_examples)
        stats.train_examples = len(train_examples)
        stats.validation_examples = len(validation_examples)
        
        # Analyze prompt variations
        system_prompts = set()
        user_prompts = set()
        categories = set()
        
        system_lengths = []
        user_lengths = []
        assistant_lengths = []
        
        for example in all_examples:
            system_prompts.add(example.system_prompt)
            user_prompts.add(example.user_input[:200])  # First 200 chars for uniqueness
            
            # Collect lengths
            system_lengths.append(len(example.system_prompt))
            user_lengths.append(len(example.user_input))
            assistant_lengths.append(len(example.assistant_response))
            
            # Collect categories
            if 'category' in example.metadata:
                categories.add(example.metadata['category'])
        
        stats.system_prompt_variations = len(system_prompts)
        stats.user_prompt_variations = len(user_prompts)
        stats.categories_covered = list(categories)
        
        # Calculate average lengths
        if system_lengths:
            stats.avg_system_prompt_length = sum(system_lengths) // len(system_lengths)
        if user_lengths:
            stats.avg_user_input_length = sum(user_lengths) // len(user_lengths)
        if assistant_lengths:
            stats.avg_assistant_response_length = sum(assistant_lengths) // len(assistant_lengths)
        
        return stats
    
    def _save_dataset_metadata(self, stats: DatasetStats, articles: List[Dict]) -> None:
        """Save dataset metadata and statistics"""
        
        metadata = {
            'dataset_stats': {
                'total_examples': stats.total_examples,
                'train_examples': stats.train_examples,
                'validation_examples': stats.validation_examples,
                'system_prompt_variations': stats.system_prompt_variations,
                'user_prompt_variations': stats.user_prompt_variations,
                'categories_covered': stats.categories_covered,
                'avg_system_prompt_length': stats.avg_system_prompt_length,
                'avg_user_input_length': stats.avg_user_input_length,
                'avg_assistant_response_length': stats.avg_assistant_response_length
            },
            'source_articles': {
                'total_articles_processed': len(articles),
                'categories_breakdown': self._get_category_breakdown(articles),
                'complexity_breakdown': self._get_complexity_breakdown(articles),
                'theme_breakdown': self._get_theme_breakdown(articles)
            },
            'generation_config': {
                'train_split_ratio': settings.TRAIN_SPLIT_RATIO,
                'max_articles_per_category': settings.MAX_ARTICLES_PER_CATEGORY,
                'min_content_length': settings.MIN_CONTENT_LENGTH
            }
        }
        
        # Save metadata
        metadata_path = os.path.join(settings.OUTPUT_DIR, 'dataset_metadata.json')
        save_json(metadata, metadata_path)
        
        logger.info(f"Saved dataset metadata to {metadata_path}")
    
    def _get_category_breakdown(self, articles: List[Dict]) -> Dict[str, int]:
        """Get breakdown of articles by category"""
        breakdown = {}
        for article in articles:
            category = article['metadata'].get('category', 'unknown')
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown
    
    def _get_complexity_breakdown(self, articles: List[Dict]) -> Dict[str, int]:
        """Get breakdown of articles by complexity"""
        breakdown = {}
        for article in articles:
            complexity = article['metadata'].get('complexity_level', 'unknown')
            breakdown[complexity] = breakdown.get(complexity, 0) + 1
        return breakdown
    
    def _get_theme_breakdown(self, articles: List[Dict]) -> Dict[str, int]:
        """Get breakdown of articles by theme"""
        breakdown = {}
        for article in articles:
            theme = article['metadata'].get('primary_theme', 'unknown')
            breakdown[theme] = breakdown.get(theme, 0) + 1
        return breakdown
    
    def validate_dataset(self, filepath: str) -> Dict[str, any]:
        """Validate generated JSONL dataset"""
        logger.info(f"Validating dataset: {filepath}")
        
        validation_results = {
            'total_examples': 0,
            'valid_examples': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            with jsonlines.open(filepath, 'r') as reader:
                for i, example in enumerate(reader):
                    validation_results['total_examples'] += 1
                    
                    # Validate structure
                    if self._validate_example_structure(example, i, validation_results):
                        validation_results['valid_examples'] += 1
        
        except Exception as e:
            validation_results['errors'].append(f"Error reading file: {str(e)}")
        
        validation_results['success_rate'] = (
            validation_results['valid_examples'] / validation_results['total_examples'] * 100
            if validation_results['total_examples'] > 0 else 0
        )
        
        logger.info(f"Validation complete: {validation_results['valid_examples']}/{validation_results['total_examples']} valid examples")
        
        return validation_results
    
    def _validate_example_structure(self, example: Dict, index: int, results: Dict) -> bool:
        """Validate individual example structure"""
        try:
            # Check required fields
            if 'messages' not in example:
                results['errors'].append(f"Example {index}: Missing 'messages' field")
                return False
            
            messages = example['messages']
            if len(messages) != 3:
                results['errors'].append(f"Example {index}: Should have exactly 3 messages")
                return False
            
            # Check message roles
            expected_roles = ['system', 'user', 'assistant']
            for i, msg in enumerate(messages):
                if 'role' not in msg or msg['role'] != expected_roles[i]:
                    results['errors'].append(f"Example {index}: Message {i} should have role '{expected_roles[i]}'")
                    return False
                
                if 'content' not in msg or not msg['content'].strip():
                    results['errors'].append(f"Example {index}: Message {i} has empty content")
                    return False
            
            # Check content lengths (warnings)
            system_len = len(messages[0]['content'])
            user_len = len(messages[1]['content'])
            assistant_len = len(messages[2]['content'])
            
            if system_len > 8000:
                results['warnings'].append(f"Example {index}: System prompt very long ({system_len} chars)")
            
            if user_len > 4000:
                results['warnings'].append(f"Example {index}: User input very long ({user_len} chars)")
            
            if assistant_len > 6000:
                results['warnings'].append(f"Example {index}: Assistant response very long ({assistant_len} chars)")
            
            return True
            
        except Exception as e:
            results['errors'].append(f"Example {index}: Validation error - {str(e)}")
            return False