import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  People,
  SportsBasketball,
  EmojiEvents,
  EventNote,
  TrendingUp,
  Block,
} from '@mui/icons-material'
import apiClient from '../api/client'

interface DashboardStats {
  users: {
    total: number
    active: number
    banned: number
    new_this_week: number
  }
  courts: {
    total: number
    active: number
  }
  tournaments: {
    total: number
    active: number
    upcoming: number
  }
  bookings: {
    total: number
    pending: number
    confirmed: number
    new_this_week: number
  }
}

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  color: string
  subtitle?: string
}

const StatCard = ({ title, value, icon, color, subtitle }: StatCardProps) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h3" component="div" color={color}>
            {value.toLocaleString()}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            backgroundColor: `${color}20`,
            borderRadius: 2,
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
)

export default function ReportsPage() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/reports/dashboard/')
      setStats(response.data)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load statistics')
      console.error('Error loading statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    )
  }

  if (!stats) {
    return (
      <Alert severity="info">No statistics available</Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {t('reports')}
      </Typography>

      {/* User Statistics */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
        {t('users')}
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('totalUsers')}
            value={stats.users.total}
            icon={<People sx={{ fontSize: 40, color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('activeUsers')}
            value={stats.users.active}
            icon={<TrendingUp sx={{ fontSize: 40, color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('bannedUsers')}
            value={stats.users.banned}
            icon={<Block sx={{ fontSize: 40, color: '#d32f2f' }} />}
            color="#d32f2f"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={`${t('newThisWeek')}`}
            value={stats.users.new_this_week}
            icon={<People sx={{ fontSize: 40, color: '#ed6c02' }} />}
            color="#ed6c02"
            subtitle={t('newThisWeek')}
          />
        </Grid>
      </Grid>

      {/* Court Statistics */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
        {t('courts')}
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('totalCourts')}
            value={stats.courts.total}
            icon={<SportsBasketball sx={{ fontSize: 40, color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('activeCourts')}
            value={stats.courts.active}
            icon={<SportsBasketball sx={{ fontSize: 40, color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
      </Grid>

      {/* Tournament Statistics */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
        {t('tournaments')}
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('totalTournaments')}
            value={stats.tournaments.total}
            icon={<EmojiEvents sx={{ fontSize: 40, color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('registrationOpen')}
            value={stats.tournaments.active}
            icon={<EmojiEvents sx={{ fontSize: 40, color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('upcoming')}
            value={stats.tournaments.upcoming}
            icon={<EmojiEvents sx={{ fontSize: 40, color: '#ed6c02' }} />}
            color="#ed6c02"
          />
        </Grid>
      </Grid>

      {/* Booking Statistics */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
        {t('bookings')}
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('totalBookings')}
            value={stats.bookings.total}
            icon={<EventNote sx={{ fontSize: 40, color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('pending')}
            value={stats.bookings.pending}
            icon={<EventNote sx={{ fontSize: 40, color: '#ed6c02' }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('confirmedBookings')}
            value={stats.bookings.confirmed}
            icon={<EventNote sx={{ fontSize: 40, color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title={t('newThisWeek')}
            value={stats.bookings.new_this_week}
            icon={<EventNote sx={{ fontSize: 40, color: '#9c27b0' }} />}
            color="#9c27b0"
            subtitle={t('newThisWeek')}
          />
        </Grid>
      </Grid>

      {/* Summary Section */}
      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          {t('summary')}
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body1" color="textSecondary">
              <strong>{t('platformGrowth')}:</strong> {stats.users.new_this_week} {t('newUsersAndBookings').split(' ')[0]} {stats.bookings.new_this_week} {t('newUsersAndBookings')}.
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body1" color="textSecondary">
              <strong>{t('activeResources')}:</strong> {stats.courts.active} {t('activeCourtsHosting')} {stats.tournaments.active} {t('ongoingTournaments')}.
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}
