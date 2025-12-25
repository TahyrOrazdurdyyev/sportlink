import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Switch,
  FormControlLabel,
  Chip,
  Alert,
  Grid,
  Card,
  CardContent,
  Divider,
} from '@mui/material'
import { Edit as EditIcon, Delete as DeleteIcon, Add as AddIcon, AttachMoney as MoneyIcon } from '@mui/icons-material'
import { useTranslation } from 'react-i18next'
import apiClient from '../api/client'

interface Feature {
  key: string
  name: Record<string, string>
  description: Record<string, string>
}

interface BookingLimits {
  bookings_per_week?: number
  max_duration_hours?: number
  allowed_days?: number[]
}

interface SubscriptionPlan {
  id: string
  name: Record<string, string>
  description: Record<string, string>
  monthly_price: number
  yearly_price: number
  currency: string
  discount_percentage: number
  discounted_monthly_price: number
  discounted_yearly_price: number
  has_discount: boolean
  features: Record<string, boolean>
  booking_limits?: BookingLimits
  order: number
  is_active: boolean
  is_popular: boolean
}

const TariffsPage = () => {
  const { t, i18n } = useTranslation()
  const currentLang = i18n.language
  
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [availableFeatures, setAvailableFeatures] = useState<Feature[]>([])
  const [loading, setLoading] = useState(true)
  const [openDialog, setOpenDialog] = useState(false)
  const [editingPlan, setEditingPlan] = useState<SubscriptionPlan | null>(null)
  const [alertMessage, setAlertMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const [formData, setFormData] = useState({
    name_tk: '',
    name_ru: '',
    name_en: '',
    description_tk: '',
    description_ru: '',
    description_en: '',
    monthly_price: '',
    yearly_price: '',
    discount_percentage: '0',
    order: '0',
    is_active: true,
    is_popular: false,
    features: {} as Record<string, boolean>,
    bookings_per_week: '',
    max_duration_hours: '',
    allowed_days: [] as number[],
  })

  useEffect(() => {
    fetchPlans()
    fetchAvailableFeatures()
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await apiClient.get('/admin/subscriptions/plans/')
      console.log('API Response:', response.data)
      const plansList = response.data.results || response.data || []
      console.log('Plans list:', plansList)
      setPlans(Array.isArray(plansList) ? plansList : [])
      setLoading(false)
    } catch (error) {
      console.error('Error fetching plans:', error)
      setLoading(false)
    }
  }

  const fetchAvailableFeatures = async () => {
    try {
      const response = await apiClient.get('/admin/subscriptions/features/')
      setAvailableFeatures(response.data)
    } catch (error) {
      console.error('Error fetching features:', error)
    }
  }

  const handleOpenDialog = (plan?: SubscriptionPlan) => {
    if (plan) {
      setEditingPlan(plan)
      setFormData({
        name_tk: plan.name.tk || '',
        name_ru: plan.name.ru || '',
        name_en: plan.name.en || '',
        description_tk: plan.description?.tk || '',
        description_ru: plan.description?.ru || '',
        description_en: plan.description?.en || '',
        monthly_price: plan.monthly_price.toString(),
        yearly_price: plan.yearly_price.toString(),
        discount_percentage: plan.discount_percentage?.toString() || '0',
        order: plan.order.toString(),
        is_active: plan.is_active,
        is_popular: plan.is_popular,
        features: plan.features,
        bookings_per_week: plan.booking_limits?.bookings_per_week?.toString() || '',
        max_duration_hours: plan.booking_limits?.max_duration_hours?.toString() || '',
        allowed_days: plan.booking_limits?.allowed_days || [],
      })
    } else {
      setEditingPlan(null)
      const defaultFeatures: Record<string, boolean> = {}
      availableFeatures.forEach(f => {
        defaultFeatures[f.key] = false
      })
      setFormData({
        name_tk: '',
        name_ru: '',
        name_en: '',
        description_tk: '',
        description_ru: '',
        description_en: '',
        monthly_price: '',
        yearly_price: '',
        discount_percentage: '0',
        order: '0',
        is_active: true,
        is_popular: false,
        features: defaultFeatures,
        bookings_per_week: '',
        max_duration_hours: '',
        allowed_days: [],
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingPlan(null)
  }

  const handleSubmit = async () => {
    const bookingLimits: BookingLimits = {}
    if (formData.bookings_per_week) {
      bookingLimits.bookings_per_week = parseInt(formData.bookings_per_week)
    }
    if (formData.max_duration_hours) {
      bookingLimits.max_duration_hours = parseFloat(formData.max_duration_hours)
    }
    if (formData.allowed_days.length > 0) {
      bookingLimits.allowed_days = formData.allowed_days
    }

    const payload = {
      name: {
        tk: formData.name_tk,
        ru: formData.name_ru,
        en: formData.name_en,
      },
      description: {
        tk: formData.description_tk,
        ru: formData.description_ru,
        en: formData.description_en,
      },
      monthly_price: parseFloat(formData.monthly_price),
      yearly_price: parseFloat(formData.yearly_price),
      discount_percentage: parseFloat(formData.discount_percentage),
      booking_limits: bookingLimits,
      order: parseInt(formData.order),
      is_active: formData.is_active,
      is_popular: formData.is_popular,
      features: formData.features,
    }

    try {
      if (editingPlan) {
        await apiClient.put(`/admin/subscriptions/plans/${editingPlan.id}/`, payload)
        setAlertMessage({ type: 'success', text: t('update') + ' successful!' })
      } else {
        await apiClient.post('/admin/subscriptions/plans/', payload)
        setAlertMessage({ type: 'success', text: t('create') + ' successful!' })
      }
      fetchPlans()
      handleCloseDialog()
    } catch (error) {
      console.error('Error saving plan:', error)
      setAlertMessage({ type: 'error', text: 'Error saving plan' })
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm(t('confirmDelete'))) {
      try {
        await apiClient.delete(`/admin/subscriptions/plans/${id}/`)
        setAlertMessage({ type: 'success', text: t('delete') + ' successful!' })
        fetchPlans()
      } catch (error) {
        console.error('Error deleting plan:', error)
        setAlertMessage({ type: 'error', text: 'Error deleting plan' })
      }
    }
  }

  const handleFeatureToggle = (featureKey: string) => {
    setFormData({
      ...formData,
      features: {
        ...formData.features,
        [featureKey]: !formData.features[featureKey],
      },
    })
  }

  const getLocalizedValue = (obj: Record<string, string> | undefined) => {
    if (!obj) return ''
    return obj[currentLang] || obj['en'] || obj['ru'] || obj['tk'] || ''
  }

  if (loading) return <Typography>{t('loading')}</Typography>

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          <MoneyIcon sx={{ fontSize: 32, mr: 1 }} />
          <Typography variant="h4">{t('tariffs')}</Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          {t('add')}
        </Button>
      </Box>

      {alertMessage && (
        <Alert severity={alertMessage.type} sx={{ mb: 2 }} onClose={() => setAlertMessage(null)}>
          {alertMessage.text}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('name')}</TableCell>
              <TableCell>{t('monthlyPrice')}</TableCell>
              <TableCell>{t('yearlyPrice')}</TableCell>
              <TableCell>{t('features')}</TableCell>
              <TableCell>Ограничения</TableCell>
              <TableCell>{t('status')}</TableCell>
              <TableCell>{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {plans.map((plan) => (
              <TableRow key={plan.id}>
                <TableCell>
                  <Box>
                    <Typography variant="body1" fontWeight="bold">
                      {getLocalizedValue(plan.name)}
                    </Typography>
                    {plan.is_popular && (
                      <Chip label={t('popular')} color="primary" size="small" sx={{ mt: 0.5 }} />
                    )}
                    {plan.has_discount && (
                      <Chip label={`-${plan.discount_percentage}%`} color="error" size="small" sx={{ mt: 0.5, ml: 0.5 }} />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  {plan.has_discount ? (
                    <Box>
                      <Typography variant="body2" sx={{ textDecoration: 'line-through', color: 'text.secondary' }}>
                        {plan.monthly_price} {plan.currency}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold" color="error">
                        {plan.discounted_monthly_price.toFixed(2)} {plan.currency}
                      </Typography>
                    </Box>
                  ) : (
                    <Typography>{plan.monthly_price} {plan.currency}</Typography>
                  )}
                </TableCell>
                <TableCell>
                  {plan.has_discount ? (
                    <Box>
                      <Typography variant="body2" sx={{ textDecoration: 'line-through', color: 'text.secondary' }}>
                        {plan.yearly_price} {plan.currency}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold" color="error">
                        {plan.discounted_yearly_price.toFixed(2)} {plan.currency}
                      </Typography>
                    </Box>
                  ) : (
                    <Typography>{plan.yearly_price} {plan.currency}</Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {Object.values(plan.features).filter(Boolean).length} / {Object.keys(plan.features).length}
                  </Typography>
                </TableCell>
                <TableCell>
                  {plan.booking_limits && (
                    <Box>
                      {plan.booking_limits.bookings_per_week && (
                        <Chip label={`${plan.booking_limits.bookings_per_week}x/нед`} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                      )}
                      {plan.booking_limits.max_duration_hours && (
                        <Chip label={`макс ${plan.booking_limits.max_duration_hours}ч`} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                      )}
                      {plan.booking_limits.allowed_days && plan.booking_limits.allowed_days.length > 0 && (
                        <Chip 
                          label={plan.booking_limits.allowed_days.length === 7 ? 'Все дни' : `${plan.booking_limits.allowed_days.length} дн`} 
                          size="small" 
                          sx={{ mb: 0.5 }} 
                        />
                      )}
                    </Box>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={plan.is_active ? t('active') : t('inactive')}
                    color={plan.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton onClick={() => handleOpenDialog(plan)} color="primary">
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDelete(plan.id)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingPlan ? t('edit') : t('add')} {t('tariffs')}
        </DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            {/* Plan Names */}
            <Typography variant="subtitle2" fontWeight="bold">
              {t('name')}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Turkmen"
                  value={formData.name_tk}
                  onChange={(e) => setFormData({ ...formData, name_tk: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Русский"
                  value={formData.name_ru}
                  onChange={(e) => setFormData({ ...formData, name_ru: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="English"
                  value={formData.name_en}
                  onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
                  fullWidth
                  required
                />
              </Grid>
            </Grid>

            {/* Descriptions */}
            <Typography variant="subtitle2" fontWeight="bold" mt={2}>
              {t('description')}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Turkmen"
                  value={formData.description_tk}
                  onChange={(e) => setFormData({ ...formData, description_tk: e.target.value })}
                  fullWidth
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Русский"
                  value={formData.description_ru}
                  onChange={(e) => setFormData({ ...formData, description_ru: e.target.value })}
                  fullWidth
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="English"
                  value={formData.description_en}
                  onChange={(e) => setFormData({ ...formData, description_en: e.target.value })}
                  fullWidth
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>

            {/* Pricing */}
            <Typography variant="subtitle2" fontWeight="bold" mt={2}>
              {t('pricing')}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label={t('monthlyPrice')}
                  value={formData.monthly_price}
                  onChange={(e) => setFormData({ ...formData, monthly_price: e.target.value })}
                  fullWidth
                  type="number"
                  required
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label={t('yearlyPrice')}
                  value={formData.yearly_price}
                  onChange={(e) => setFormData({ ...formData, yearly_price: e.target.value })}
                  fullWidth
                  type="number"
                  required
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Скидка (%)"
                  value={formData.discount_percentage}
                  onChange={(e) => {
                    const value = parseFloat(e.target.value) || 0
                    if (value >= 0 && value <= 100) {
                      setFormData({ ...formData, discount_percentage: e.target.value })
                    }
                  }}
                  fullWidth
                  type="number"
                  inputProps={{ min: 0, max: 100, step: 1 }}
                  helperText="0-100%"
                />
              </Grid>
            </Grid>

            {/* Discount Preview */}
            {parseFloat(formData.discount_percentage) > 0 && formData.monthly_price && formData.yearly_price && (
              <Card variant="outlined" sx={{ mt: 2, bgcolor: 'error.light', borderColor: 'error.main' }}>
                <CardContent>
                  <Typography variant="subtitle2" fontWeight="bold" color="error.dark" gutterBottom>
                    💰 Цены со скидкой {formData.discount_percentage}%
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Месячная цена:
                      </Typography>
                      <Typography variant="body2" sx={{ textDecoration: 'line-through' }}>
                        {formData.monthly_price} TMT
                      </Typography>
                      <Typography variant="h6" color="error.dark" fontWeight="bold">
                        {(parseFloat(formData.monthly_price) * (1 - parseFloat(formData.discount_percentage) / 100)).toFixed(2)} TMT
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Годовая цена:
                      </Typography>
                      <Typography variant="body2" sx={{ textDecoration: 'line-through' }}>
                        {formData.yearly_price} TMT
                      </Typography>
                      <Typography variant="h6" color="error.dark" fontWeight="bold">
                        {(parseFloat(formData.yearly_price) * (1 - parseFloat(formData.discount_percentage) / 100)).toFixed(2)} TMT
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            )}

            {/* Features */}
            <Typography variant="subtitle2" fontWeight="bold" mt={2}>
              {t('features')}
            </Typography>
            <Card variant="outlined">
              <CardContent>
                {availableFeatures.map((feature) => (
                  <Box key={feature.key} mb={1}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={formData.features[feature.key] || false}
                          onChange={() => handleFeatureToggle(feature.key)}
                        />
                      }
                      label={
                        <Box>
                          <Typography variant="body1">{getLocalizedValue(feature.name)}</Typography>
                          <Typography variant="caption" color="textSecondary">
                            {getLocalizedValue(feature.description)}
                          </Typography>
                        </Box>
                      }
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>

            <Divider sx={{ my: 2 }} />

            {/* Booking Restrictions */}
            <Typography variant="subtitle2" fontWeight="bold" mt={2} gutterBottom>
              📅 Ограничения бронирования
            </Typography>
            <Card variant="outlined" sx={{ bgcolor: 'info.lighter', borderColor: 'info.main' }}>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Бронирований в неделю"
                      value={formData.bookings_per_week}
                      onChange={(e) => setFormData({ ...formData, bookings_per_week: e.target.value })}
                      fullWidth
                      type="number"
                      inputProps={{ min: 0, step: 1 }}
                      helperText="Сколько раз можно бронировать в неделю (0 = без ограничений)"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      label="Макс. продолжительность (часы)"
                      value={formData.max_duration_hours}
                      onChange={(e) => setFormData({ ...formData, max_duration_hours: e.target.value })}
                      fullWidth
                      type="number"
                      inputProps={{ min: 0, step: 0.5 }}
                      helperText="Максимальная длительность одного бронирования (0 = без ограничений)"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" gutterBottom>
                      Разрешенные дни недели:
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {[
                        { value: 1, label: 'Пн' },
                        { value: 2, label: 'Вт' },
                        { value: 3, label: 'Ср' },
                        { value: 4, label: 'Чт' },
                        { value: 5, label: 'Пт' },
                        { value: 6, label: 'Сб' },
                        { value: 7, label: 'Вс' },
                      ].map((day) => (
                        <Chip
                          key={day.value}
                          label={day.label}
                          onClick={() => {
                            const newDays = formData.allowed_days.includes(day.value)
                              ? formData.allowed_days.filter(d => d !== day.value)
                              : [...formData.allowed_days, day.value].sort()
                            setFormData({ ...formData, allowed_days: newDays })
                          }}
                          color={formData.allowed_days.includes(day.value) ? 'primary' : 'default'}
                          variant={formData.allowed_days.includes(day.value) ? 'filled' : 'outlined'}
                        />
                      ))}
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                      Пустой список = все дни разрешены
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Divider sx={{ my: 2 }} />

            {/* Settings */}
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <TextField
                  label={t('order')}
                  value={formData.order}
                  onChange={(e) => setFormData({ ...formData, order: e.target.value })}
                  fullWidth
                  type="number"
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    />
                  }
                  label={t('active')}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_popular}
                      onChange={(e) => setFormData({ ...formData, is_popular: e.target.checked })}
                    />
                  }
                  label={t('popular')}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{t('cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {editingPlan ? t('update') : t('create')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TariffsPage
