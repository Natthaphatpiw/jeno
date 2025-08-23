'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import toast from 'react-hot-toast';
import { ImageSlot, UploadedImage } from '../types';

interface ImageUploaderProps {
  imageSlot: ImageSlot;
  onImageUpload: (slotId: string, image: UploadedImage) => void;
  onImageRemove: (slotId: string) => void;
  uploadedImage?: UploadedImage;
}

export default function ImageUploader({
  imageSlot,
  onImageUpload,
  onImageRemove,
  uploadedImage,
}: ImageUploaderProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    },
    multiple: false,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        const preview = URL.createObjectURL(file);
        
        const newImage: UploadedImage = {
          id: Date.now().toString(),
          file,
          preview,
          slotId: imageSlot.id,
        };
        
        onImageUpload(imageSlot.id, newImage);
        toast.success('Image uploaded successfully');
      }
    },
    onDropRejected: () => {
      toast.error('Please upload a valid image file');
    },
  });

  const handleRemoveImage = () => {
    if (uploadedImage) {
      URL.revokeObjectURL(uploadedImage.preview);
      onImageRemove(imageSlot.id);
      toast.success('Image removed');
    }
  };

  return (
    <div className="bg-white/95 backdrop-blur-sm border border-navy-200 rounded-xl p-4 hover:border-sky-300 transition-all duration-300 hover:shadow-lg">
      <div className="mb-4">
        <div className="flex items-start justify-between mb-3 gap-2">
          <h4 className="text-base font-bold text-dark-navy-800 leading-tight flex-1 min-w-0">
            <span className="block truncate" title={imageSlot.id}>
              {imageSlot.id.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
            </span>
          </h4>
          <span className="text-xs font-medium text-sky-600 bg-sky-100 px-2 py-1 rounded-full whitespace-nowrap">
            {imageSlot.suggestedType}
          </span>
        </div>
        
        <div className="space-y-2">
          <p className="text-sm text-navy-600 leading-relaxed line-clamp-2" title={imageSlot.description}>
            {imageSlot.description}
          </p>
          
          {imageSlot.placementRationale && (
            <details className="group">
              <summary className="text-xs font-semibold text-sky-700 cursor-pointer hover:text-sky-800 py-1">
                💡 Why this image belongs here
              </summary>
              <div className="bg-sky-50 border border-sky-200 rounded-lg p-2 mt-1">
                <p className="text-xs text-sky-600 leading-relaxed">{imageSlot.placementRationale}</p>
              </div>
            </details>
          )}
          
          {imageSlot.contentGuidance && (
            <details className="group">
              <summary className="text-xs font-semibold text-navy-700 cursor-pointer hover:text-navy-800 py-1">
                📋 Content recommendations
              </summary>
              <div className="bg-navy-50 border border-navy-200 rounded-lg p-2 mt-1">
                <p className="text-xs text-navy-600 leading-relaxed">{imageSlot.contentGuidance}</p>
              </div>
            </details>
          )}
          
          <div className="flex flex-wrap gap-1">
            {imageSlot.dimensions && (
              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                📐 {imageSlot.dimensions}
              </span>
            )}
            {imageSlot.aspectRatio && (
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
                📏 {imageSlot.aspectRatio}
              </span>
            )}
          </div>
          
          {imageSlot.alternatives && (
            <details className="group">
              <summary className="text-xs font-semibold text-gray-600 cursor-pointer hover:text-gray-800 py-1">
                🔀 Alternative options
              </summary>
              <div className="text-xs text-gray-600 mt-1 p-2 bg-gray-50 rounded-lg border border-gray-200">
                {imageSlot.alternatives}
              </div>
            </details>
          )}
        </div>
      </div>

      {uploadedImage ? (
        <div className="relative">
          <img
            src={uploadedImage.preview}
            alt="Uploaded image"
            className="w-full h-32 object-cover rounded-lg shadow-sm"
          />
          <button
            onClick={handleRemoveImage}
            className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all duration-200 shadow-md"
          >
            <X className="w-3 h-3" />
          </button>
          <div className="mt-2 p-2 bg-sky-50 rounded-lg border border-sky-200">
            <div className="text-xs font-medium text-dark-navy-700 truncate" title={uploadedImage.file.name}>
              {uploadedImage.file.name}
            </div>
            <div className="text-xs text-navy-500">
              {(uploadedImage.file.size / 1024).toFixed(1)} KB
            </div>
          </div>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? 'border-sky-400 bg-sky-50'
              : 'border-navy-300 hover:border-sky-400 hover:bg-sky-50/30'
          }`}
        >
          <input {...getInputProps()} />
          <div className={`w-10 h-10 rounded-xl mx-auto mb-2 flex items-center justify-center ${
            isDragActive ? 'bg-sky-100' : 'bg-navy-100'
          }`}>
            <ImageIcon className={`w-5 h-5 ${isDragActive ? 'text-sky-600' : 'text-navy-400'}`} />
          </div>
          <p className="text-sm font-medium text-navy-700 mb-1">
            {isDragActive ? 'Drop image here...' : 'Click or drag to upload'}
          </p>
          <p className="text-xs text-navy-500">
            Images only • Enhance your article
          </p>
        </div>
      )}
    </div>
  );
}