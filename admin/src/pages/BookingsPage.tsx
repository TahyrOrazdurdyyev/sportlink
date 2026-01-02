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
  Chip,
  TextField,
  MenuItem,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Refresh as RefreshIcon } from '@mui/icons-material'
import apiClient from '../api/client'

interface Booking {
  id: string
  court_id: string
  court_name: { tk?: string; ru?: string; en?: string }
  user_id: string
  user_phone: string
  user_name: string
  start_time: string
  end_time: string
  duration_hours: number
  status: string
  payment_status: string
  total_price: number
  equipment_rental: { [key: string]: number }
  equipment_quantity: number
  find_opponents: boolean
  opponents_needed: number
  created_at: string
}

interface Statistics {
  total_bookings: number
  today_bookings: number
  week_bookings: number
  month_bookings: number
  pending_bookings: number
  confirmed_bookings: number
  cancelled_bookings: number
  completed_bookings: number
}

export default function BookingsPage() {
  const { t, i18n } = useTranslation()
  const currentLang = i18n.language

  const [bookings, setBookings] = useState<Booking[]>([])
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  useEffect(() => {
    fetchBookings()
    fetchStatistics()
  }, [statusFilter, startDate, endDate])

  const fetchBookings = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (statusFilter) params.status = statusFilter
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      const response = await apiClient.get('/admin/bookings/', { params })
      setBookings(response.data.bookings || [])
      setError('')
    } catch (err: any) {
      console.error('Error fetching bookings:', err)
      setError(err.response?.data?.error || 'Failed to load bookings')
    } finally {
      setLoading(false)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await apiClient.get('/admin/bookings/statistics/')
      setStatistics(response.data)
    } catch (err: any) {
      console.error('Error fetching statistics:', err)
    }
  }

  const getLocalizedCourtName = (name_i18n: { tk?: string; ru?: string; en?: string }) => {
    return name_i18n?.[currentLang as keyof typeof name_i18n] || name_i18n?.ru || name_i18n?.en || name_i18n?.tk || '-'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'success'
      case 'pending':
        return 'warning'
      case 'cancelled':
        return 'error'
      case 'completed':
        return 'info'
      default:
        return 'default'
    }
  }

  const getPaymentStatusColor = (paymentStatus: string) => {
    switch (paymentStatus) {
      case 'paid':
        return 'success'
      case 'pending':
        return 'warning'
      case 'refunded':
        return 'error'
      default:
        return 'default'
    }
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString(currentLang, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          {t('bookings')}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={() => {
            fetchBookings()
            fetchStatistics()
          }}
        >
          {t('refresh')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  {t('totalBookings')}
                </Typography>
                <Typography variant="h5">{statistics.total_bookings}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  {t('todayBookings')}
                </Typography>
                <Typography variant="h5">{statistics.today_bookings}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  {t('weekBookings')}
                </Typography>
                <Typography variant="h5">{statistics.week_bookings}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  {t('monthBookings')}
                </Typography>
                <Typography variant="h5">{statistics.month_bookings}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              select
              label={t('status')}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              size="small"
            >
              <MenuItem value="">{t('all')}</MenuItem>
              <MenuItem value="pending">{t('pending')}</MenuItem>
              <MenuItem value="confirmed">{t('confirmed')}</MenuItem>
              <MenuItem value="cancelled">{t('cancelled')}</MenuItem>
              <MenuItem value="completed">{t('completed')}</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="date"
              label={t('startDate')}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              type="date"
              label={t('endDate')}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              size="small"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Bookings Table */}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>{t('court')}</TableCell>
              <TableCell>{t('user')}</TableCell>
              <TableCell>{t('dateTime')}</TableCell>
              <TableCell>{t('duration')}</TableCell>
              <TableCell>{t('status')}</TableCell>
              <TableCell>{t('payment')}</TableCell>
              <TableCell>{t('price')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <CircularProgress size={24} sx={{ my: 2 }} />
                </TableCell>
              </TableRow>
            ) : bookings.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ my: 2 }}>
                    {t('noBookings')}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              bookings.map((booking) => (
                <TableRow key={booking.id}>
                  <TableCell>
                    <Typography variant="body2">
                      {getLocalizedCourtName(booking.court_name)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {booking.user_name || '-'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {booking.user_phone}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDateTime(booking.start_time)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {booking.duration_hours.toFixed(1)} {t('hours')}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={t(booking.status)} 
                      size="small" 
                      color={getStatusColor(booking.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={t(booking.payment_status)} 
                      size="small" 
                      color={getPaymentStatusColor(booking.payment_status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {booking.total_price} TMT
                    </Typography>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

