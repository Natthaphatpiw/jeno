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
    <div className="bg-white/95 backdrop-blur-sm border-2 border-navy-200 rounded-2xl p-6 hover:border-sky-400 transition-all duration-300 hover:shadow-xl">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-bold text-dark-navy-800 capitalize">
            {imageSlot.position}
          </h4>
          <span className="text-xs font-semibold text-sky-600 bg-sky-100 px-3 py-1.5 rounded-full">
            {imageSlot.suggestedType}
          </span>
        </div>
        <p className="text-sm text-navy-600 leading-relaxed">
          {imageSlot.description}
        </p>
      </div>

      {uploadedImage ? (
        <div className="relative">
          <img
            src={uploadedImage.preview}
            alt="Uploaded image"
            className="w-full h-40 object-cover rounded-xl shadow-md"
          />
          <button
            onClick={handleRemoveImage}
            className="absolute top-3 right-3 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-all duration-200 transform hover:scale-110 shadow-lg"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="mt-4 p-4 bg-sky-50 rounded-xl border border-sky-200">
            <div className="text-sm font-semibold text-dark-navy-700 mb-1">{uploadedImage.file.name}</div>
            <div className="text-xs text-navy-500">
              {(uploadedImage.file.size / 1024).toFixed(1)} KB • Image uploaded successfully
            </div>
          </div>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-300 ${
            isDragActive
              ? 'border-sky-400 bg-sky-50 shadow-lg'
              : 'border-navy-300 hover:border-sky-400 hover:bg-sky-50/30'
          }`}
        >
          <input {...getInputProps()} />
          <div className={`w-12 h-12 rounded-2xl mx-auto mb-3 flex items-center justify-center ${
            isDragActive ? 'bg-sky-100' : 'bg-navy-100'
          }`}>
            <ImageIcon className={`w-6 h-6 ${isDragActive ? 'text-sky-600' : 'text-navy-400'}`} />
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