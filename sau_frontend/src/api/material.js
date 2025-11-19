import { http } from '@/utils/request'

// 素材管理API
export const materialApi = {
  // 获取所有素材
  getAllMaterials: () => {
    return http.get('/getFiles')
  },
  
  // 上传素材
  uploadMaterial: (formData, onUploadProgress) => {
    // 使用http.upload方法，它已经配置了正确的Content-Type
    return http.upload('/uploadSave', formData, onUploadProgress)
  },
  
  // 删除素材
  deleteMaterial: (id) => {
    return http.get(`/deleteFile?id=${id}`)
  },
  
  // 下载素材
  downloadMaterial: (filePath) => {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'}/download/${filePath}`
  },
  
  // 获取素材预览URL
  getMaterialPreviewUrl: (filename) => {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'}/getFile?filename=${filename}`
  },

  // 文件夹监控相关 API
  // 获取当前监控的文件夹配置
  getWatchFolder: () => {
    return http.get('/getWatchFolder')
  },

  // 设置并开始监控文件夹
  setWatchFolder: (folderPath) => {
    return http.post('/setWatchFolder', { folderPath })
  },

  // 停止文件夹监控
  stopWatchFolder: () => {
    return http.post('/stopWatchFolder')
  }
}