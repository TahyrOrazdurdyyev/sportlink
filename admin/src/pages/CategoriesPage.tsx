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
  parent_id?: string | null
  children_count: number
  created_at: string
  updated_at: string
}

export default function CategoriesPage() {
  const { t, i18n } = useTranslation()
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

  const getLocalizedName = (name_i18n: { tk?: string; ru?: string; en?: string }) => {
    const lang = i18n.language as 'tk' | 'ru' | 'en'
    return name_i18n[lang] || name_i18n.tk || name_i18n.ru || name_i18n.en || '-'
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
          {editingCategory ? 'Edit Category' : 'Create Category'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Turkmen
            </Typography>
            <TextField
              fullWidth
              label="Name (Turkmen)"
              value={formData.name_tk}
              onChange={(e) => setFormData({ ...formData, name_tk: e.target.value })}
              margin="dense"
              required
            />
            <TextField
              fullWidth
              label="Description (Turkmen)"
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
              label="Name (Russian)"
              value={formData.name_ru}
              onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
              margin="dense"
            />
            <TextField
              fullWidth
              label="Description (Russian)"
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
              label="Name (English)"
              value={formData.name_en}
              onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
              margin="dense"
            />
            <TextField
              fullWidth
              label="Description (English)"
              value={formData.description_en}
              onChange={(e) => setFormData({ ...formData, description_en: e.target.value })}
              margin="dense"
              multiline
              rows={2}
            />
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
        <DialogTitle>Delete Category</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{categoryToDelete?.name_i18n.tk || categoryToDelete?.name_i18n.ru || categoryToDelete?.name_i18n.en}"?
          </Typography>
          {categoryToDelete && categoryToDelete.children_count > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This category has {categoryToDelete.children_count} child categories!
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
