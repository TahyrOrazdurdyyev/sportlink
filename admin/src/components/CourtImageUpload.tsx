import React, { useState } from 'react';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

interface CourtImageUploadProps {
  courtId: string;
  images: string[];
  onImagesChange: (images: string[]) => void;
}

export const CourtImageUpload: React.FC<CourtImageUploadProps> = ({
  courtId,
  images,
  onImagesChange,
}) => {
  const token = useAuthStore((state) => state.token);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    // Check token
    if (!token) {
      alert('Ошибка: нет токена авторизации. Попробуйте выйти и войти заново.');
      return;
    }

    // Check if adding these files would exceed the limit
    if (images.length + files.length > 10) {
      alert('Максимум 10 фотографий на площадку');
      return;
    }

    setUploading(true);
    const newImages = [...images];

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
          alert(`Файл ${file.name} слишком большой. Максимум 5MB`);
          continue;
        }

        // Validate file type
        if (!file.type.match(/image\/(jpeg|jpg|png|webp)/)) {
          alert(`Файл ${file.name} имеет неподдерживаемый формат. Разрешены: JPEG, PNG, WebP`);
          continue;
        }

        const formData = new FormData();
        formData.append('court_id', courtId);
        formData.append('image', file);

        const response = await axios.post(
          'http://localhost:8000/api/v1/admin/courts/upload-image/',
          formData,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
              const progress = progressEvent.total
                ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
                : 0;
              setUploadProgress(progress);
            },
          }
        );

        if (response.data.url) {
          newImages.push(response.data.url);
        }
      }

      onImagesChange(newImages);
    } catch (error: any) {
      console.error('Upload error:', error);
      alert(error.response?.data?.error || 'Ошибка загрузки фотографии');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDelete = async (index: number) => {
    if (!confirm('Удалить это фото?')) return;

    try {
      await axios.delete(
        `http://localhost:8000/api/v1/admin/courts/${courtId}/images/${index}/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      const newImages = images.filter((_, i) => i !== index);
      onImagesChange(newImages);
    } catch (error: any) {
      console.error('Delete error:', error);
      alert(error.response?.data?.error || 'Ошибка удаления фотографии');
    }
  };

  return (
    <div style={{ marginTop: '20px' }}>
      <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>
        Фотографии площадки ({images.length}/10)
      </label>

      {/* Image Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
          gap: '15px',
          marginBottom: '15px',
        }}
      >
        {images.map((url, index) => (
          <div
            key={index}
            style={{
              position: 'relative',
              paddingTop: '100%',
              borderRadius: '8px',
              overflow: 'hidden',
              border: '2px solid #ddd',
            }}
          >
            <img
              src={url}
              alt={`Court ${index + 1}`}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
            <button
              onClick={() => handleDelete(index)}
              style={{
                position: 'absolute',
                top: '5px',
                right: '5px',
                background: 'rgba(255, 0, 0, 0.8)',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '30px',
                height: '30px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px',
                fontWeight: 'bold',
              }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Upload Button */}
      {images.length < 10 && (
        <div>
          <input
            type="file"
            multiple
            accept="image/jpeg,image/jpg,image/png,image/webp"
            onChange={handleFileChange}
            disabled={uploading}
            style={{ display: 'none' }}
            id="court-image-upload"
          />
          <label
            htmlFor="court-image-upload"
            style={{
              display: 'inline-block',
              padding: '10px 20px',
              background: uploading ? '#ccc' : '#FF6B35',
              color: 'white',
              borderRadius: '4px',
              cursor: uploading ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
            }}
          >
            {uploading ? `Загрузка... ${uploadProgress}%` : '+ Добавить фото'}
          </label>
          <p style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
            Максимум 10 фотографий. Форматы: JPEG, PNG, WebP. Размер: до 5MB
          </p>
        </div>
      )}
    </div>
  );
};

