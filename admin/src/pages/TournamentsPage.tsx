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
  People as PeopleIcon,
} from '@mui/icons-material'
import apiClient from '../api/client'

interface Tournament {
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
  image_url?: string
  country?: string
  city?: string
  organizer_name?: string
  registration_link?: string
  start_date: string
  end_date: string
  registration_deadline?: string
  max_participants: number
  min_participants: number
  registration_open: boolean
  registration_fee: number
  status: string
  participant_count: number
  created_at: string
  updated_at: string
}

const STATUS_OPTIONS = [
  { value: 'draft', label: 'Draft' },
  { value: 'open', label: 'Registration Open' },
  { value: 'closed', label: 'Registration Closed' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]

export default function TournamentsPage() {
  const { t, i18n } = useTranslation()
  const [tournaments, setTournaments] = useState<Tournament[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingTournament, setEditingTournament] = useState<Tournament | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [tournamentToDelete, setTournamentToDelete] = useState<Tournament | null>(null)
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [uploadingImage, setUploadingImage] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    name_tk: '',
    name_ru: '',
    name_en: '',
    description_tk: '',
    description_ru: '',
    description_en: '',
    country: '',
    city: '',
    organizer_name: '',
    registration_link: '',
    start_date: '',
    end_date: '',
    registration_deadline: '',
    max_participants: '32',
    min_participants: '8',
    registration_fee: '0',
    registration_open: true,
    status: 'draft',
  })

  const loadTournaments = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await apiClient.get('/admin/tournaments/')
      setTournaments(response.data.results || [])
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load tournaments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTournaments()
  }, [])

  const handleOpenDialog = (tournament?: Tournament) => {
    if (tournament) {
      setEditingTournament(tournament)
      setFormData({
        name_tk: tournament.name_i18n.tk || '',
        name_ru: tournament.name_i18n.ru || '',
        name_en: tournament.name_i18n.en || '',
        description_tk: tournament.description_i18n?.tk || '',
        description_ru: tournament.description_i18n?.ru || '',
        description_en: tournament.description_i18n?.en || '',
        country: tournament.country || '',
        city: tournament.city || '',
        organizer_name: tournament.organizer_name || '',
        registration_link: tournament.registration_link || '',
        start_date: tournament.start_date ? new Date(tournament.start_date).toISOString().slice(0, 16) : '',
        end_date: tournament.end_date ? new Date(tournament.end_date).toISOString().slice(0, 16) : '',
        registration_deadline: tournament.registration_deadline ? new Date(tournament.registration_deadline).toISOString().slice(0, 16) : '',
        max_participants: tournament.max_participants?.toString() || '32',
        min_participants: tournament.min_participants?.toString() || '8',
        registration_fee: tournament.registration_fee?.toString() || '0',
        registration_open: tournament.registration_open,
        status: tournament.status || 'draft',
      })
      setImagePreview(tournament.image_url || null)
    } else {
      setEditingTournament(null)
      setFormData({
        name_tk: '',
        name_ru: '',
        name_en: '',
        description_tk: '',
        description_ru: '',
        description_en: '',
        country: '',
        city: '',
        organizer_name: '',
        registration_link: '',
        start_date: '',
        end_date: '',
        registration_deadline: '',
        max_participants: '32',
        min_participants: '8',
        registration_fee: '0',
        registration_open: true,
        status: 'draft',
      })
      setImagePreview(null)
    }
    setSelectedImage(null)
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingTournament(null)
    setSelectedImage(null)
    setImagePreview(null)
  }

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('Image file size cannot exceed 10MB')
        return
      }
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUploadImage = async (tournamentId: string) => {
    if (!selectedImage) return

    try {
      setUploadingImage(true)
      const formData = new FormData()
      formData.append('image', selectedImage)

      await apiClient.post(`/admin/tournaments/${tournamentId}/upload-image/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSelectedImage(null)
      await loadTournaments()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to upload image')
    } finally {
      setUploadingImage(false)
    }
  }

  const handleDeleteImage = async (tournamentId: string) => {
    try {
      await apiClient.delete(`/admin/tournaments/${tournamentId}/delete-image/`)
      setImagePreview(null)
      await loadTournaments()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete image')
    }
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
        country: formData.country,
        city: formData.city,
        organizer_name: formData.organizer_name,
        registration_link: formData.registration_link || null,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
        registration_deadline: formData.registration_deadline ? new Date(formData.registration_deadline).toISOString() : null,
        max_participants: parseInt(formData.max_participants),
        min_participants: parseInt(formData.min_participants),
        registration_fee: parseFloat(formData.registration_fee),
        registration_open: formData.registration_open,
        status: formData.status,
      }

      let tournamentId: string
      if (editingTournament) {
        await apiClient.patch(`/admin/tournaments/${editingTournament.id}/`, payload)
        tournamentId = editingTournament.id
      } else {
        const response = await apiClient.post('/admin/tournaments/', payload)
        tournamentId = response.data.id
      }

      // Upload image if selected
      if (selectedImage) {
        await handleUploadImage(tournamentId)
      }

      handleCloseDialog()
      loadTournaments()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to save tournament')
    }
  }

  const handleDeleteClick = (tournament: Tournament) => {
    setTournamentToDelete(tournament)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!tournamentToDelete) return

    try {
      setError('')
      await apiClient.delete(`/admin/tournaments/${tournamentToDelete.id}/`)
      setDeleteDialogOpen(false)
      setTournamentToDelete(null)
      loadTournaments()
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to delete tournament')
      setDeleteDialogOpen(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, any> = {
      draft: 'default',
      open: 'success',
      closed: 'warning',
      in_progress: 'info',
      completed: 'default',
      cancelled: 'error',
    }
    return colors[status] || 'default'
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
          {t('tournaments')}
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('addTournament')}
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
              <TableCell>{t('startDate')}</TableCell>
              <TableCell>{t('participants')}</TableCell>
              <TableCell>{t('fee')}</TableCell>
              <TableCell>{t('status')}</TableCell>
              <TableCell>{t('created')}</TableCell>
              <TableCell align="right">{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tournaments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No tournaments found. Add your first tournament!
                </TableCell>
              </TableRow>
            ) : (
              tournaments.map((tournament) => (
                <TableRow key={tournament.id}>
                  <TableCell>
                    {getLocalizedName(tournament.name_i18n)}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(tournament.start_date).toLocaleDateString()}
                      {' - '}
                      {new Date(tournament.end_date).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <PeopleIcon fontSize="small" color="action" />
                      <Typography variant="body2">
                        {tournament.participant_count} / {tournament.max_participants}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {tournament.registration_fee > 0 ? `${tournament.registration_fee} TMT` : 'Free'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={tournament.status}
                      size="small"
                      color={getStatusColor(tournament.status)}
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(tournament.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(tournament)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(tournament)}
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
          {editingTournament ? 'Edit Tournament' : 'Create Tournament'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Tournament Names
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
              label="Name (Russian)"
              value={formData.name_ru}
              onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
              margin="dense"
            />
            <TextField
              fullWidth
              label="Name (English)"
              value={formData.name_en}
              onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
              margin="dense"
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Description
            </Typography>
            <TextField
              fullWidth
              label="Description (Turkmen)"
              value={formData.description_tk}
              onChange={(e) => setFormData({ ...formData, description_tk: e.target.value })}
              margin="dense"
              multiline
              rows={2}
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
            <TextField
              fullWidth
              label="Description (English)"
              value={formData.description_en}
              onChange={(e) => setFormData({ ...formData, description_en: e.target.value })}
              margin="dense"
              multiline
              rows={2}
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Tournament Image
            </Typography>
            <Box sx={{ mb: 2 }}>
              {imagePreview && (
                <Box sx={{ mb: 2, position: 'relative', display: 'inline-block' }}>
                  <img
                    src={imagePreview}
                    alt="Tournament"
                    style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '8px' }}
                  />
                  {editingTournament && editingTournament.image_url && !selectedImage && (
                    <IconButton
                      sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        bgcolor: 'error.main',
                        color: 'white',
                        '&:hover': { bgcolor: 'error.dark' },
                      }}
                      size="small"
                      onClick={() => handleDeleteImage(editingTournament.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>
              )}
              <Button variant="outlined" component="label">
                {imagePreview ? 'Change Image' : 'Upload Image'}
                <input
                  type="file"
                  hidden
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  onChange={handleImageSelect}
                />
              </Button>
              {selectedImage && (
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Selected: {selectedImage.name}
                </Typography>
              )}
            </Box>

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Location
            </Typography>
            <Box display="flex" gap={2}>
              <TextField
                fullWidth
                label="Country"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                margin="dense"
              />
              <TextField
                fullWidth
                label="City"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                margin="dense"
              />
            </Box>

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Organizer
            </Typography>
            <TextField
              fullWidth
              label="Organizer Name"
              value={formData.organizer_name}
              onChange={(e) => setFormData({ ...formData, organizer_name: e.target.value })}
              margin="dense"
              helperText="e.g., Sportlink Platform, Tennis Club, etc."
            />
            <TextField
              fullWidth
              label="Registration Link (Optional)"
              value={formData.registration_link}
              onChange={(e) => setFormData({ ...formData, registration_link: e.target.value })}
              margin="dense"
              type="url"
              helperText="External link for registration or more info"
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Schedule
            </Typography>
            <TextField
              fullWidth
              label="Start Date & Time"
              type="datetime-local"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              margin="dense"
              InputLabelProps={{ shrink: true }}
              required
            />
            <TextField
              fullWidth
              label="End Date & Time"
              type="datetime-local"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              margin="dense"
              InputLabelProps={{ shrink: true }}
              required
            />
            <TextField
              fullWidth
              label="Registration Deadline"
              type="datetime-local"
              value={formData.registration_deadline}
              onChange={(e) => setFormData({ ...formData, registration_deadline: e.target.value })}
              margin="dense"
              InputLabelProps={{ shrink: true }}
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Participants & Fee
            </Typography>
            <Box display="flex" gap={2}>
              <TextField
                fullWidth
                label="Min Participants"
                type="number"
                value={formData.min_participants}
                onChange={(e) => setFormData({ ...formData, min_participants: e.target.value })}
                margin="dense"
                inputProps={{ min: 1 }}
                required
              />
              <TextField
                fullWidth
                label="Max Participants"
                type="number"
                value={formData.max_participants}
                onChange={(e) => setFormData({ ...formData, max_participants: e.target.value })}
                margin="dense"
                inputProps={{ min: 1 }}
                required
              />
            </Box>
            <TextField
              fullWidth
              label="Registration Fee (TMT)"
              type="number"
              value={formData.registration_fee}
              onChange={(e) => setFormData({ ...formData, registration_fee: e.target.value })}
              margin="dense"
              inputProps={{ min: 0, step: 0.01 }}
            />

            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Status
            </Typography>
            <TextField
              fullWidth
              select
              label="Status"
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              margin="dense"
              required
            >
              {STATUS_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>

            <FormControlLabel
              control={
                <Switch
                  checked={formData.registration_open}
                  onChange={(e) => setFormData({ ...formData, registration_open: e.target.checked })}
                />
              }
              label="Registration Open"
              sx={{ mt: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              !formData.start_date ||
              !formData.end_date ||
              (!formData.name_tk && !formData.name_ru && !formData.name_en)
            }
          >
            {editingTournament ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Tournament</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "
            {tournamentToDelete?.name_i18n.tk ||
              tournamentToDelete?.name_i18n.ru ||
              tournamentToDelete?.name_i18n.en}
            "?
          </Typography>
          {tournamentToDelete && tournamentToDelete.participant_count > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This tournament has {tournamentToDelete.participant_count} participants!
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
