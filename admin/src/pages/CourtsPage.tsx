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
  MenuItem,
  Switch,
  FormControlLabel,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
} from '@mui/icons-material'
import apiClient from '../api/client'
import { CourtImageUpload } from '../components/CourtImageUpload'

interface Court {
  id: string
  name_i18n: {
    tk?: string
    ru?: string
    en?: string
  }
  address: string
  type: string
  attributes?: Record<string, any>
  images?: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Category {
  id: string
  name_i18n: {
    tk?: string
    ru?: string
    en?: string
  }
}

export default function CourtsPage() {
  const { t, i18n } = useTranslation()
  const [courts, setCourts] = useState<Court[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingCourt, setEditingCourt] = useState<Court | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [courtToDelete, setCourtToDelete] = useState<Court | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    name_tk: '',
    name_ru: '',
    name_en: '',
    address: '',
    type: '',
    is_active: true,
    images: [] as string[],
  })

  const loadCourts = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await apiClient.get('/admin/courts/')
      setCourts(response.data.results || [])
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load courts')
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/categories/')
      setCategories(response.data.results || response.data)
    } catch (err: any) {
      console.error('Failed to load categories:', err)
    }
  }

  useEffect(() => {
    loadCourts()
    loadCategories()
  }, [])

  const handleOpenDialog = (court?: Court) => {
    if (court) {
      setEditingCourt(court)
      setFormData({
        name_tk: court.name_i18n.tk || '',
        name_ru: court.name_i18n.ru || '',
        name_en: court.name_i18n.en || '',
        address: court.address || '',
        type: court.type || '',
        is_active: court.is_active,
        images: court.images || [],
      })
    } else {
      setEditingCourt(null)
      setFormData({
        name_tk: '',
        name_ru: '',
        name_en: '',
        address: '',
        type: '',
        is_active: true,
        images: [],
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingCourt(null)
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
        address: formData.address,
        type: formData.type,
        is_active: formData.is_active,
        attributes: {},
        images: formData.images, // Передаем актуальный массив фото
      }

      if (editingCourt) {
        await apiClient.patch(`/admin/courts/${editingCourt.id}/`, payload)
      } else {
        await apiClient.post('/admin/courts/', payload)
      }

      handleCloseDialog()
      loadCourts()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save court')
    }
  }

  const handleDeleteClick = (court: Court) => {
    setCourtToDelete(court)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!courtToDelete) return

    try {
      setError('')
      await apiClient.delete(`/admin/courts/${courtToDelete.id}/`)
      setDeleteDialogOpen(false)
      setCourtToDelete(null)
      loadCourts()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete court')
      setDeleteDialogOpen(false)
    }
  }

  const getLocalizedName = (name_i18n: { tk?: string; ru?: string; en?: string }) => {
    const lang = i18n.language as 'tk' | 'ru' | 'en'
    return name_i18n[lang] || name_i18n.tk || name_i18n.ru || name_i18n.en || '-'
  }

  const getCategoryName = (categoryId: string) => {
    // Если это старый тип (tennis, football, etc.), просто вернуть его
    const oldTypes = ['tennis', 'football', 'basketball', 'volleyball', 'gym', 'other']
    if (oldTypes.includes(categoryId)) {
      return categoryId
    }
    
    // Иначе искать в категориях
    const category = categories.find(c => c.id === categoryId)
    return category ? getLocalizedName(category.name_i18n) : categoryId
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
          {t('courts')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('addCourt')}
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
              <TableCell>{t('name')}</TableCell>
              <TableCell>{t('address')}</TableCell>
              <TableCell>{t('type')}</TableCell>
              <TableCell>{t('status')}</TableCell>
              <TableCell>{t('created')}</TableCell>
              <TableCell align="right">{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {courts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No courts found. Add your first court!
                </TableCell>
              </TableRow>
            ) : (
              courts.map((court) => (
                <TableRow key={court.id}>
                  <TableCell>
                    {getLocalizedName(court.name_i18n)}
                  </TableCell>
                  <TableCell>{court.address}</TableCell>
                  <TableCell>
                    <Chip label={getCategoryName(court.type)} size="small" />
                  </TableCell>
                  <TableCell>
                    {court.is_active ? (
                      <Chip
                        icon={<ActiveIcon />}
                        label={t('active')}
                        color="success"
                        size="small"
                      />
                    ) : (
                      <Chip
                        icon={<InactiveIcon />}
                        label={t('inactive')}
                        color="default"
                        size="small"
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(court.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(court)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(court)}
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
          {editingCourt ? t('editCourt') : t('createCourt')}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {t('courtNames')}
            </Typography>
            <TextField
              fullWidth
              label={t('nameTurkmen') + ' *'}
              value={formData.name_tk}
              onChange={(e) => setFormData({ ...formData, name_tk: e.target.value })}
              margin="dense"
              required
            />
            <TextField
              fullWidth
              label={t('nameRussian')}
              value={formData.name_ru}
              onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
              margin="dense"
            />
            <TextField
              fullWidth
              label={t('nameEnglish')}
              value={formData.name_en}
              onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
              margin="dense"
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              {t('details')}
            </Typography>
            <TextField
              fullWidth
              label={t('address') + ' *'}
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              margin="dense"
              required
            />
            <TextField
              fullWidth
              select
              label={t('type') + ' *'}
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              margin="dense"
              required
            >
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {getLocalizedName(category.name_i18n)}
                </MenuItem>
              ))}
            </TextField>

            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
              }
              label={t('active')}
              sx={{ mt: 2 }}
            />

            {/* Image Upload - only show when editing existing court */}
            {editingCourt ? (
              <CourtImageUpload
                courtId={editingCourt.id}
                images={formData.images}
                onImagesChange={(newImages) => setFormData({ ...formData, images: newImages })}
              />
            ) : (
              <Alert severity="info" sx={{ mt: 2 }}>
                💡 Чтобы добавить фотографии, сначала создайте площадку, затем откройте её на редактирование
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{t('cancel')}</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !formData.address ||
              (!formData.name_tk && !formData.name_ru && !formData.name_en)
            }
          >
            {editingCourt ? t('update') : t('create')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Court</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "
            {courtToDelete?.name_i18n.tk ||
              courtToDelete?.name_i18n.ru ||
              courtToDelete?.name_i18n.en}
            "?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This action cannot be undone!
          </Alert>
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
