import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import apiClient from '../api/client'

interface Category {
  id: string
  name_i18n: {
    tk?: string
    ru?: string
    en?: string
  }
  description_i18n: {
    tk?: string
    ru?: string
    en?: string
  }
  available_equipment?: Array<{
    key: string
    name_i18n: {
      tk?: string
      ru?: string
      en?: string
    }
  }>
  parent_id?: string | null
  children_count: number
  created_at: string
  updated_at: string
}

export default function CategoriesPage() {
  const { t } = useTranslation()
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name_tk: '',
    name_ru: '',
    name_en: '',
    description_tk: '',
    description_ru: '',
    description_en: '',
  })
  
  // Equipment state
  const [equipmentItems, setEquipmentItems] = useState<Array<{
    key: string
    name_tk: string
    name_ru: string
    name_en: string
  }>>([])
  
  const addEquipmentItem = () => {
    setEquipmentItems([...equipmentItems, {
      key: '',
      name_tk: '',
      name_ru: '',
      name_en: ''
    }])
  }
  
  const removeEquipmentItem = (index: number) => {
    setEquipmentItems(equipmentItems.filter((_, i) => i !== index))
  }
  
  const updateEquipmentItem = (index: number, field: string, value: string) => {
    const updated = [...equipmentItems]
    updated[index] = { ...updated[index], [field]: value }
    setEquipmentItems(updated)
  }

  const loadCategories = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await apiClient.get('/categories/')
      // API returns paginated response with 'results' field
      setCategories(response.data.results || [])
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load categories')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCategories()
  }, [])

  const handleOpenDialog = (category?: Category) => {
    if (category) {
      setEditingCategory(category)
      setFormData({
        name_tk: category.name_i18n.tk || '',
        name_ru: category.name_i18n.ru || '',
        name_en: category.name_i18n.en || '',
        description_tk: category.description_i18n.tk || '',
        description_ru: category.description_i18n.ru || '',
        description_en: category.description_i18n.en || '',
      })
      // Load equipment
      if (category.available_equipment && category.available_equipment.length > 0) {
        setEquipmentItems(category.available_equipment.map(eq => ({
          key: eq.key,
          name_tk: eq.name_i18n.tk || '',
          name_ru: eq.name_i18n.ru || '',
          name_en: eq.name_i18n.en || ''
        })))
      } else {
        setEquipmentItems([])
      }
    } else {
      setEditingCategory(null)
      setFormData({
        name_tk: '',
        name_ru: '',
        name_en: '',
        description_tk: '',
        description_ru: '',
        description_en: '',
      })
      setEquipmentItems([])
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingCategory(null)
    setFormData({
      name_tk: '',
      name_ru: '',
      name_en: '',
      description_tk: '',
      description_ru: '',
      description_en: '',
    })
    setEquipmentItems([])
  }

  const handleSubmit = async () => {
    try {
      setError('')
      
      const payload = {
        name_i18n: {
          tk: formData.name_tk,
          ru: formData.name_ru,
          en: formData.name_en,
        },
        description_i18n: {
          tk: formData.description_tk,
          ru: formData.description_ru,
          en: formData.description_en,
        },
        available_equipment: equipmentItems
          .filter(item => item.key.trim() !== '')
          .map(item => ({
            key: item.key.trim(),
            name_i18n: {
              tk: item.name_tk.trim(),
              ru: item.name_ru.trim(),
              en: item.name_en.trim()
            }
          }))
      }

      if (editingCategory) {
        await apiClient.patch(`/categories/${editingCategory.id}/`, payload)
      } else {
        await apiClient.post('/categories/', payload)
      }

      handleCloseDialog()
      loadCategories()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save category')
    }
  }

  const handleDeleteClick = (category: Category) => {
    setCategoryToDelete(category)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!categoryToDelete) return

    try {
      setError('')
      await apiClient.delete(`/categories/${categoryToDelete.id}/`)
      setDeleteDialogOpen(false)
      setCategoryToDelete(null)
      loadCategories()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete category')
      setDeleteDialogOpen(false)
    }
  }


  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          {t('categories')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('addCategory')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('name')} (TK)</TableCell>
              <TableCell>{t('name')} (RU)</TableCell>
              <TableCell>{t('name')} (EN)</TableCell>
              <TableCell>{t('childrenCount')}</TableCell>
              <TableCell>{t('created')}</TableCell>
              <TableCell align="right">{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {categories.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No categories found. Add your first category!
                </TableCell>
              </TableRow>
            ) : (
              categories.map((category) => (
                <TableRow key={category.id}>
                  <TableCell>{category.name_i18n.tk || '-'}</TableCell>
                  <TableCell>{category.name_i18n.ru || '-'}</TableCell>
                  <TableCell>{category.name_i18n.en || '-'}</TableCell>
                  <TableCell>
                    {category.children_count > 0 && (
                      <Chip label={category.children_count} size="small" color="primary" />
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(category.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(category)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(category)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCategory ? t('editCategory') : t('createCategory')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Turkmen
            </Typography>
            <TextField
              fullWidth
              label={t('nameTurkmen')}
              value={formData.name_tk}
              onChange={(e) => setFormData({ ...formData, name_tk: e.target.value })}
              margin="dense"
              required
            />
            <TextField
              fullWidth
              label={t('descriptionTurkmen')}
              value={formData.description_tk}
              onChange={(e) => setFormData({ ...formData, description_tk: e.target.value })}
              margin="dense"
              multiline
              rows={2}
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Russian
            </Typography>
            <TextField
              fullWidth
              label={t('nameRussian')}
              value={formData.name_ru}
              onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
              margin="dense"
            />
            <TextField
              fullWidth
              label={t('descriptionRussian')}
              value={formData.description_ru}
              onChange={(e) => setFormData({ ...formData, description_ru: e.target.value })}
              margin="dense"
              multiline
              rows={2}
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              English
            </Typography>
            <TextField
              fullWidth
              label={t('nameEnglish')}
              value={formData.name_en}
              onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
              margin="dense"
            />
            <TextField
              fullWidth
              label={t('descriptionEnglish')}
              value={formData.description_en}
              onChange={(e) => setFormData({ ...formData, description_en: e.target.value })}
              margin="dense"
              multiline
              rows={2}
            />
            
            {/* Equipment Section */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 3, mb: 1, fontWeight: 'bold' }}>
              {t('availableEquipment')}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {t('equipmentDescription')}
            </Typography>
            
            {equipmentItems.map((item, index) => (
              <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1, bgcolor: '#f9f9f9' }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle2">Equipment Item #{index + 1}</Typography>
                  <IconButton size="small" color="error" onClick={() => removeEquipmentItem(index)}>
                    <DeleteIcon />
                  </IconButton>
                </Box>
                
                <TextField
                  fullWidth
                  label={t('equipmentKey')}
                  value={item.key}
                  onChange={(e) => updateEquipmentItem(index, 'key', e.target.value)}
                  margin="dense"
                  size="small"
                  required
                  helperText="Use lowercase, e.g.: balls, rackets, shin_guards"
                />
                
                <Box display="flex" gap={1} mt={1}>
                  <TextField
                    fullWidth
                    label={t('nameTurkmen')}
                    value={item.name_tk}
                    onChange={(e) => updateEquipmentItem(index, 'name_tk', e.target.value)}
                    margin="dense"
                    size="small"
                  />
                  <TextField
                    fullWidth
                    label={t('nameRussian')}
                    value={item.name_ru}
                    onChange={(e) => updateEquipmentItem(index, 'name_ru', e.target.value)}
                    margin="dense"
                    size="small"
                  />
                  <TextField
                    fullWidth
                    label={t('nameEnglish')}
                    value={item.name_en}
                    onChange={(e) => updateEquipmentItem(index, 'name_en', e.target.value)}
                    margin="dense"
                    size="small"
                  />
                </Box>
              </Box>
            ))}
            
            <Button
              startIcon={<AddIcon />}
              onClick={addEquipmentItem}
              variant="outlined"
              size="small"
              sx={{ mt: 1 }}
            >
              {t('addEquipment')}
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.name_tk && !formData.name_ru && !formData.name_en}
          >
            {editingCategory ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>{t('deleteCategory')}</DialogTitle>
        <DialogContent>
          <Typography>
            {t('deleteCategoryConfirm')} "{categoryToDelete?.name_i18n.tk || categoryToDelete?.name_i18n.ru || categoryToDelete?.name_i18n.en}"?
          </Typography>
          {categoryToDelete && categoryToDelete.children_count > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {t('categoryHasChildren')}: {categoryToDelete.children_count}!
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
