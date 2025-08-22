#!/usr/bin/env python3
"""
Jenosize Article Scraping and Fine-tuning Data Pipeline
Main orchestrator for the entire data collection and processing pipeline.
"""

import os
import sys
import time
import argparse
from typing import List, Dict, Optional
from datetime import datetime

from config.settings import settings
from scrapers.category_scraper import CategoryScraper
from scrapers.article_scraper import ArticleScraper
from processors.content_extractor import ContentExtractor
from generators.dataset_builder import DatasetBuilder
from models.schemas import ProcessingStats, ArticleLink, ScrapingResult
from utils.logger import get_logger
from utils.helpers import save_json, load_json, ensure_dir_exists
from utils.csv_reader import CSVReader

logger = get_logger(__name__)

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, resume_from_step: Optional[str] = None):
        self.resume_from_step = resume_from_step
        self.stats = ProcessingStats()
        self.start_time = time.time()
        
        # Initialize components
        self.csv_reader = CSVReader()
        self.category_scraper = CategoryScraper()  # Keep for backward compatibility
        self.article_scraper = ArticleScraper(use_selenium=True)  # Enable Selenium
        self.content_extractor = ContentExtractor()
        self.dataset_builder = DatasetBuilder()
        
        # Ensure output directories exist
        ensure_dir_exists(settings.OUTPUT_DIR)
        ensure_dir_exists(settings.RAW_DIR)
        ensure_dir_exists(settings.PROCESSED_DIR)
    
    def run_pipeline(self, max_articles_per_category: Optional[int] = None) -> None:
        """Run the complete data pipeline"""
        
        logger.info("=" * 60)
        logger.info("🚀 Starting Jenosize Article Scraping Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Discover articles
            article_links = self._step_1_discover_articles()
            
            # Step 2: Scrape articles
            scraping_results = self._step_2_scrape_articles(article_links, max_articles_per_category)
            
            # Step 3: Process content
            processed_articles = self._step_3_process_content(scraping_results)
            
            # Step 4: Build datasets
            dataset_stats = self._step_4_build_datasets(processed_articles)
            
            # Step 5: Validate and finalize
            self._step_5_finalize(dataset_stats)
            
        except KeyboardInterrupt:
            logger.warning("⏹️  Pipeline interrupted by user")
            self._cleanup()
        except Exception as e:
            logger.error(f"💥 Pipeline failed with error: {e}")
            raise
        finally:
            self._cleanup()
    
    def _step_1_discover_articles(self) -> List[ArticleLink]:
        """Step 1: Load article links from CSV file"""
        
        step_name = "discover_articles"
        cache_file = os.path.join(settings.OUTPUT_DIR, "article_links.json")
        
        if self._should_skip_step(step_name, cache_file):
            logger.info("📂 Loading cached article links...")
            cached_data = load_json(cache_file)
            if cached_data:
                return [ArticleLink(**link_data) for link_data in cached_data['links']]
        
        logger.info("🔍 Step 1: Loading articles from CSV file")
        
        try:
            # Read article links from CSV
            article_links = self.csv_reader.read_urls()
            
            if not article_links:
                logger.error("No articles found in CSV file")
                return []
            
            # Get category breakdown
            category_stats = self.csv_reader.get_category_stats(article_links)
            
            # Update statistics
            self.stats.total_categories = category_stats['total_categories']
            self.stats.total_links_found = len(article_links)
            self.stats.categories_breakdown = category_stats['by_category']
            
            # Save results
            links_data = {
                'discovery_time': datetime.now().isoformat(),
                'total_links': len(article_links),
                'category_stats': category_stats,
                'links': [
                    {
                        'url': link.url,
                        'title': link.title,
                        'category': link.category,
                        'href': link.href
                    }
                    for link in article_links
                ]
            }
            
            save_json(links_data, cache_file)
            
            logger.info(f"✅ Loaded {len(article_links)} articles from CSV across {len(category_stats['by_category'])} categories")
            
            # Log category breakdown
            for category, count in category_stats['by_category'].items():
                logger.info(f"   📑 {category}: {count} articles")
            
            return article_links
            
        except Exception as e:
            logger.error(f"❌ Step 1 failed: {e}")
            raise
    
    def _step_2_scrape_articles(self, 
                               article_links: List[ArticleLink], 
                               max_articles_per_category: Optional[int] = None) -> List[ScrapingResult]:
        """Step 2: Scrape article content"""
        
        step_name = "scrape_articles"
        cache_file = os.path.join(settings.OUTPUT_DIR, "scraping_results.json")
        
        if self._should_skip_step(step_name, cache_file):
            logger.info("📂 Loading cached scraping results...")
            cached_data = load_json(cache_file)
            if cached_data:
                results = []
                for result_data in cached_data['results']:
                    # Reconstruct scraping results (simplified)
                    result = ScrapingResult(
                        success=result_data['success'],
                        url=result_data['url'],
                        error=result_data.get('error'),
                        processing_time=result_data.get('processing_time', 0)
                    )
                    results.append(result)
                return results
        
        logger.info(f"📰 Step 2: Scraping {len(article_links)} articles")
        
        # Limit articles if specified
        if max_articles_per_category:
            original_count = len(article_links)
            article_links = self._limit_articles_per_category(article_links, max_articles_per_category)
            logger.info(f"   📊 Limited to {len(article_links)}/{original_count} articles ({max_articles_per_category} per category)")
        
        try:
            # Scrape articles
            scraping_results = self.article_scraper.scrape_articles(article_links)
            
            # Update statistics
            self.stats.total_articles_scraped = len(scraping_results)
            self.stats.successful_scrapes = sum(1 for r in scraping_results if r.success)
            self.stats.failed_scrapes = self.stats.total_articles_scraped - self.stats.successful_scrapes
            
            # Calculate content statistics
            total_content_chars = 0
            for result in scraping_results:
                if result.success and result.content:
                    content_length = len(result.content.text_content)
                    total_content_chars += content_length
            
            self.stats.total_content_chars = total_content_chars
            
            # Save results (simplified for caching)
            results_data = {
                'scraping_time': datetime.now().isoformat(),
                'total_scraped': len(scraping_results),
                'successful': self.stats.successful_scrapes,
                'failed': self.stats.failed_scrapes,
                'results': [
                    {
                        'success': result.success,
                        'url': result.url,
                        'error': result.error,
                        'processing_time': result.processing_time,
                        'has_content': result.content is not None
                    }
                    for result in scraping_results
                ]
            }
            
            save_json(results_data, cache_file)
            
            logger.info(f"✅ Scraping completed: {self.stats.successful_scrapes}/{len(scraping_results)} successful")
            logger.info(f"   📊 Success rate: {self.stats.success_rate:.1f}%")
            logger.info(f"   📝 Total content: {total_content_chars:,} characters")
            
            return scraping_results
            
        except Exception as e:
            logger.error(f"❌ Step 2 failed: {e}")
            raise
    
    def _step_3_process_content(self, scraping_results: List[ScrapingResult]) -> List[Dict]:
        """Step 3: Process scraped content for training"""
        
        logger.info("⚙️  Step 3: Processing content for training data")
        
        processed_articles = []
        
        # Filter successful results
        successful_results = [r for r in scraping_results if r.success and r.content]
        
        logger.info(f"   📊 Processing {len(successful_results)} successfully scraped articles")
        
        for result in successful_results:
            try:
                if not result.content:
                    continue
                
                # Convert to dict for processing
                content_dict = {
                    'metadata': {
                        'url': result.content.metadata.url,
                        'title': result.content.metadata.title,
                        'category': result.content.metadata.category,
                        'author': result.content.metadata.author,
                        'publish_date': result.content.metadata.publish_date,
                        'description': result.content.metadata.description,
                        'tags': result.content.metadata.tags,
                        'content_stats': result.content.metadata.content_stats
                    },
                    'html_content': result.content.html_content,
                    'text_content': result.content.text_content,
                    'structured_content': result.content.structured_content,
                    'images': result.content.images
                }
                
                processed_articles.append(content_dict)
                
            except Exception as e:
                logger.warning(f"Error processing article {result.url}: {e}")
                continue
        
        logger.info(f"✅ Content processing completed: {len(processed_articles)} articles ready for training")
        
        return processed_articles
    
    def _step_4_build_datasets(self, processed_articles: List[Dict]) -> Dict:
        """Step 4: Build training and validation datasets"""
        
        logger.info("🏗️  Step 4: Building training datasets")
        
        try:
            # Build datasets
            dataset_stats = self.dataset_builder.build_datasets(processed_articles)
            
            logger.info(f"✅ Dataset building completed:")
            logger.info(f"   📚 Training examples: {dataset_stats.train_examples}")
            logger.info(f"   🔍 Validation examples: {dataset_stats.validation_examples}")
            logger.info(f"   🎯 Categories covered: {len(dataset_stats.categories_covered)}")
            logger.info(f"   📏 Avg system prompt: {dataset_stats.avg_system_prompt_length} chars")
            logger.info(f"   📏 Avg user input: {dataset_stats.avg_user_input_length} chars")
            logger.info(f"   📏 Avg assistant response: {dataset_stats.avg_assistant_response_length} chars")
            
            return dataset_stats
            
        except Exception as e:
            logger.error(f"❌ Step 4 failed: {e}")
            raise
    
    def _step_5_finalize(self, dataset_stats: Dict) -> None:
        """Step 5: Validate datasets and create final report"""
        
        logger.info("🎯 Step 5: Finalizing and validating datasets")
        
        try:
            # Validate datasets
            train_validation = self.dataset_builder.validate_dataset(
                os.path.join(settings.OUTPUT_DIR, 'train.jsonl')
            )
            
            val_validation = self.dataset_builder.validate_dataset(
                os.path.join(settings.OUTPUT_DIR, 'validation.jsonl')
            )
            
            # Calculate final statistics
            self.stats.processing_time_seconds = time.time() - self.start_time
            
            # Create final report
            self._create_final_report(dataset_stats, train_validation, val_validation)
            
            logger.info("✅ Pipeline completed successfully!")
            logger.info(f"   ⏱️  Total processing time: {self.stats.processing_time_seconds:.1f} seconds")
            logger.info(f"   📊 Success rate: {self.stats.success_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Step 5 failed: {e}")
            raise
    
    def _create_final_report(self, dataset_stats: Dict, train_validation: Dict, val_validation: Dict) -> None:
        """Create final pipeline report"""
        
        report = {
            'pipeline_summary': {
                'execution_time': datetime.now().isoformat(),
                'processing_time_seconds': self.stats.processing_time_seconds,
                'total_categories_scraped': self.stats.total_categories,
                'total_links_discovered': self.stats.total_links_found,
                'total_articles_scraped': self.stats.total_articles_scraped,
                'successful_scrapes': self.stats.successful_scrapes,
                'failed_scrapes': self.stats.failed_scrapes,
                'success_rate_percent': self.stats.success_rate,
                'total_content_characters': self.stats.total_content_chars,
                'categories_breakdown': self.stats.categories_breakdown
            },
            'dataset_stats': dataset_stats.__dict__ if hasattr(dataset_stats, '__dict__') else dataset_stats,
            'validation_results': {
                'train_dataset': train_validation,
                'validation_dataset': val_validation
            },
            'output_files': {
                'train_dataset': os.path.join(settings.OUTPUT_DIR, 'train.jsonl'),
                'validation_dataset': os.path.join(settings.OUTPUT_DIR, 'validation.jsonl'),
                'dataset_metadata': os.path.join(settings.OUTPUT_DIR, 'dataset_metadata.json'),
                'raw_html_files': settings.RAW_DIR,
                'processed_content': settings.PROCESSED_DIR
            }
        }
        
        # Save report
        report_path = os.path.join(settings.OUTPUT_DIR, 'pipeline_report.json')
        save_json(report, report_path)
        
        logger.info(f"📋 Final report saved to: {report_path}")
    
    def _should_skip_step(self, step_name: str, cache_file: str) -> bool:
        """Check if step should be skipped due to resume logic"""
        if not self.resume_from_step:
            return False
        
        step_order = ['discover_articles', 'scrape_articles', 'process_content', 'build_datasets', 'finalize']
        
        if step_name not in step_order:
            return False
        
        current_step_index = step_order.index(step_name)
        resume_step_index = step_order.index(self.resume_from_step) if self.resume_from_step in step_order else -1
        
        # Skip if current step is before resume step and cache exists
        return current_step_index < resume_step_index and os.path.exists(cache_file)
    
    def _limit_articles_per_category(self, 
                                   article_links: List[ArticleLink], 
                                   max_per_category: int) -> List[ArticleLink]:
        """Limit number of articles per category"""
        
        category_counts = {}
        limited_links = []
        
        for link in article_links:
            category = link.category
            if category not in category_counts:
                category_counts[category] = 0
            
            if category_counts[category] < max_per_category:
                limited_links.append(link)
                category_counts[category] += 1
        
        return limited_links
    
    def _cleanup(self) -> None:
        """Cleanup resources"""
        try:
            self.category_scraper.close()
            self.article_scraper.close()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Jenosize Article Scraping and Fine-tuning Data Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Run full pipeline
  python main.py --limit 10                # Limit to 10 articles per category
  python main.py --resume process_content  # Resume from content processing
  python main.py --limit 5 --resume scrape_articles  # Resume with limits
        """
    )
    
    parser.add_argument(
        '--limit', 
        type=int, 
        help='Maximum articles per category (useful for development/testing)'
    )
    
    parser.add_argument(
        '--resume', 
        choices=['discover_articles', 'scrape_articles', 'process_content', 'build_datasets', 'finalize'],
        help='Resume pipeline from specific step (uses cached data where available)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Custom output directory (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Override output directory if specified
    if args.output_dir:
        settings.OUTPUT_DIR = os.path.abspath(args.output_dir)
        settings.RAW_DIR = os.path.join(settings.OUTPUT_DIR, "raw")
        settings.PROCESSED_DIR = os.path.join(settings.OUTPUT_DIR, "processed")
        logger.info(f"Using custom output directory: {settings.OUTPUT_DIR}")
    
    try:
        # Initialize and run pipeline
        pipeline = DataPipeline(resume_from_step=args.resume)
        pipeline.run_pipeline(max_articles_per_category=args.limit)
        
    except KeyboardInterrupt:
        logger.info("👋 Pipeline interrupted. Goodbye!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()