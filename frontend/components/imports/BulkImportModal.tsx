'use client'

import { useState } from 'react'
import { X, Upload, Download, AlertCircle } from 'lucide-react'

interface BulkImportModalProps {
  isOpen: boolean
  onClose: () => void
  onImport: (file: File) => Promise<void>
  onSuccess?: () => void
}

export default function BulkImportModal({ isOpen, onClose, onImport, onSuccess }: BulkImportModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
        setError('لطفاً فایل CSV یا Excel انتخاب کنید')
        return
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('حجم فایل نباید بیشتر از 10 مگابایت باشد')
        return
      }

      setSelectedFile(file)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    setError(null)

    try {
      await onImport(selectedFile)
      onSuccess?.()
      onClose()
    } catch (error) {
      setError('خطا در آپلود فایل. لطفاً دوباره تلاش کنید')
    } finally {
      setUploading(false)
    }
  }

  const downloadTemplate = () => {
    // Create a simple CSV template
    const template = `name,description,price,stock,category_id,image_url,tags
محصول نمونه,توضیحات محصول,100000,10,1,https://example.com/image.jpg,برچسب1,برچسب2`
    
    const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'product_template.csv'
    link.click()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">ورود دسته‌جمعی محصولات</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              انتخاب فایل
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <span className="mt-2 block text-sm font-medium text-gray-900">
                  کلیک کنید یا فایل را بکشید
                </span>
                <span className="mt-1 block text-xs text-gray-500">
                  CSV یا Excel تا 10MB
                </span>
              </label>
            </div>
            {selectedFile && (
              <div className="mt-2 text-sm text-gray-600">
                فایل انتخاب شده: {selectedFile.name}
              </div>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          )}

          {/* Template Download */}
          <div className="text-center">
            <button
              onClick={downloadTemplate}
              className="flex items-center gap-2 mx-auto text-sm text-blue-600 hover:text-blue-800 transition-colors"
            >
              <Download size={16} />
              دانلود قالب CSV
            </button>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              انصراف
            </button>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? 'در حال آپلود...' : 'آپلود'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
} 