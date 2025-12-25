import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  MenuItem,
} from '@mui/material'
import { Edit, Delete, Block, CheckCircle } from '@mui/icons-material'
import apiClient from '../api/client'

interface User {
  id: string
  phone: string
  nickname?: string
  email?: string
  first_name?: string
  last_name?: string
  is_active: boolean
  is_banned: boolean
  is_staff: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  last_active_at?: string
  subscription_plan?: {
    en?: string
    ru?: string
    tk?: string
  }
  subscription_end_date?: string
  subscription_status?: string
}

interface SubscriptionRequest {
  id: string
  user_id: string
  user_phone: string
  user_name: string
  plan_id: string
  plan_name: string
  period: string
  amount: number
  status: string
  user_notes?: string
  admin_notes?: string
  rejection_reason?: string
  created_at: string
  updated_at: string
  approved_at?: string
  rejected_at?: string
}

export default function UsersPage() {
  const { t } = useTranslation()
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [pendingRequests, setPendingRequests] = useState<SubscriptionRequest[]>([])
  const [userRequests, setUserRequests] = useState<Map<string, number>>(new Map())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [requestDialogOpen, setRequestDialogOpen] = useState(false)
  const [subscriptionDialogOpen, setSubscriptionDialogOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [selectedUserRequests, setSelectedUserRequests] = useState<SubscriptionRequest[]>([])
  const [subscriptionPlans, setSubscriptionPlans] = useState<any[]>([])
  const [subscriptionFormData, setSubscriptionFormData] = useState({
    plan_id: '',
    duration_days: 30,
  })

  // Form state
  const [formData, setFormData] = useState({
    phone: '',
    email: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_banned: false,
    is_staff: false,
    is_superuser: false,
  })

  // Fetch users and pending requests
  const fetchUsers = async () => {
    try {
      setLoading(true)
      const [usersResponse, requestsResponse] = await Promise.all([
        apiClient.get('/admin/users/'),
        apiClient.get('/subscriptions/requests/pending/')
      ])
      
      const usersData = usersResponse.data.results || usersResponse.data
      console.log('Users data loaded:', usersData) // Debug: check subscription data
      console.log('First user data:', {
        phone: usersData[0]?.phone,
        nickname: usersData[0]?.nickname,
        first_name: usersData[0]?.first_name,
        last_name: usersData[0]?.last_name,
        subscription_plan: usersData[0]?.subscription_plan,
        subscription_end_date: usersData[0]?.subscription_end_date
      })
      setUsers(usersData)
      setFilteredUsers(usersData)
      setPendingRequests(requestsResponse.data)
      
      // Create a map of user_id -> count of pending requests
      const requestsMap = new Map<string, number>()
      requestsResponse.data.forEach((req: SubscriptionRequest) => {
        requestsMap.set(req.user_id, (requestsMap.get(req.user_id) || 0) + 1)
      })
      setUserRequests(requestsMap)
      
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load data')
      console.error('Error loading data:', err)
      console.error('Error details:', err.response?.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
    fetchSubscriptionPlans()
  }, [])

  const fetchSubscriptionPlans = async () => {
    try {
      const response = await apiClient.get('/admin/subscriptions/plans/')
      setSubscriptionPlans(response.data.results || response.data)
    } catch (err: any) {
      console.error('Error loading subscription plans:', err)
    }
  }

  // Filter users based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredUsers(users)
      return
    }

    const query = searchQuery.toLowerCase().trim()
    const filtered = users.filter((user) => {
      // Search by phone
      if (user.phone.toLowerCase().includes(query)) {
        return true
      }
      
      // Search by nickname
      if (user.nickname && user.nickname.toLowerCase().includes(query)) {
        return true
      }
      
      // Search by email
      if (user.email && user.email.toLowerCase().includes(query)) {
        return true
      }
      
      // Search by first name
      if (user.first_name && user.first_name.toLowerCase().includes(query)) {
        return true
      }
      
      // Search by last name
      if (user.last_name && user.last_name.toLowerCase().includes(query)) {
        return true
      }
      
      // Search by full name
      const fullName = `${user.first_name || ''} ${user.last_name || ''}`.toLowerCase().trim()
      if (fullName.includes(query)) {
        return true
      }
      
      return false
    })
    
    setFilteredUsers(filtered)
  }, [searchQuery, users])

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditingUser(user)
      setFormData({
        phone: user.phone,
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        is_active: user.is_active,
        is_banned: user.is_banned,
        is_staff: user.is_staff,
        is_superuser: user.is_superuser,
      })
    } else {
      setEditingUser(null)
      setFormData({
        phone: '',
        email: '',
        first_name: '',
        last_name: '',
        is_active: true,
        is_banned: false,
        is_staff: false,
        is_superuser: false,
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingUser(null)
  }

  const handleSubmit = async () => {
    try {
      const payload = {
        phone: formData.phone,
        email: formData.email || null,
        first_name: formData.first_name,
        last_name: formData.last_name,
        is_active: formData.is_active,
        is_banned: formData.is_banned,
        is_staff: formData.is_staff,
        is_superuser: formData.is_superuser,
      }

      if (editingUser) {
        await apiClient.put(`/admin/users/${editingUser.id}/`, payload)
      } else {
        await apiClient.post('/admin/users/', payload)
      }

      fetchUsers()
      handleCloseDialog()
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to save user')
      console.error('Error saving user:', err)
    }
  }

  const handleDelete = async () => {
    if (!editingUser) return

    try {
      await apiClient.delete(`/admin/users/${editingUser.id}/`)
      fetchUsers()
      setDeleteDialogOpen(false)
      setEditingUser(null)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete user')
      console.error('Error deleting user:', err)
    }
  }

  const handleOpenDeleteDialog = (user: User) => {
    setEditingUser(user)
    setDeleteDialogOpen(true)
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleDateString()
  }

  const handleViewUserRequests = (user: User) => {
    const requests = pendingRequests.filter(req => req.user_id === user.id)
    setSelectedUserRequests(requests)
    setEditingUser(user)
    setRequestDialogOpen(true)
  }

  const handleApproveRequest = async (requestId: string) => {
    try {
      await apiClient.post(`/subscriptions/requests/${requestId}/approve/`, {
        admin_notes: 'Approved from admin panel'
      })
      fetchUsers() // Reload data
      setRequestDialogOpen(false)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to approve request')
      console.error('Error approving request:', err)
    }
  }

  const handleRejectRequest = async (requestId: string) => {
    const reason = prompt('Enter rejection reason:')
    if (!reason) return

    try {
      await apiClient.post(`/subscriptions/requests/${requestId}/reject/`, {
        rejection_reason: reason
      })
      fetchUsers() // Reload data
      setRequestDialogOpen(false)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to reject request')
      console.error('Error rejecting request:', err)
    }
  }

  const handleOpenSubscriptionDialog = (user: User) => {
    setEditingUser(user)
    setSubscriptionFormData({
      plan_id: subscriptionPlans[0]?.id || '',
      duration_days: 30,
    })
    setSubscriptionDialogOpen(true)
  }

  const handleCreateSubscription = async () => {
    if (!editingUser) return

    try {
      await apiClient.post('/subscriptions/admin/create-manual/', {
        user_id: editingUser.id,
        plan_id: subscriptionFormData.plan_id,
        duration_days: subscriptionFormData.duration_days,
      })
      
      setSubscriptionDialogOpen(false)
      setError('')
      alert(`Subscription created successfully for ${editingUser.phone}`)
      
      // Reload data after a short delay to ensure backend has processed
      setTimeout(() => {
        fetchUsers()
      }, 500)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create subscription')
      console.error('Error creating subscription:', err)
    }
  }

  const handleCancelSubscription = async (user: User) => {
    if (!window.confirm(`Are you sure you want to cancel the subscription for ${user.phone}?`)) {
      return
    }

    try {
      await apiClient.delete(`/subscriptions/admin/user/${user.id}/cancel/`)
      fetchUsers() // Reload data
      setError('')
      alert(`Subscription cancelled successfully for ${user.phone}`)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to cancel subscription')
      console.error('Error cancelling subscription:', err)
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">{t('users')}</Typography>
        <Button variant="contained" color="primary" onClick={() => handleOpenDialog()}>
          {t('addUser')}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Search Bar */}
      <Box mb={3}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search by phone, nickname, first name, or last name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <Box sx={{ mr: 1, display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  🔍
                </Typography>
              </Box>
            ),
            endAdornment: searchQuery && (
              <IconButton
                size="small"
                onClick={() => setSearchQuery('')}
                edge="end"
              >
                ✕
              </IconButton>
            ),
          }}
        />
        {searchQuery && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Found {filteredUsers.length} user(s)
          </Typography>
        )}
      </Box>

      <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ minWidth: 120 }}>{t('phone')}</TableCell>
              <TableCell sx={{ minWidth: 150 }}>{t('name')}</TableCell>
              <TableCell sx={{ minWidth: 100 }}>{t('status')}</TableCell>
              <TableCell sx={{ minWidth: 140 }}>Subscription</TableCell>
              <TableCell sx={{ minWidth: 110 }}>Expires</TableCell>
              <TableCell sx={{ minWidth: 80 }} align="center">Requests</TableCell>
              <TableCell sx={{ minWidth: 120 }} align="right">{t('actions')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : filteredUsers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  {searchQuery ? 'No users found matching your search' : 'No users found'}
                </TableCell>
              </TableRow>
            ) : (
              filteredUsers.map((user) => (
                <TableRow key={user.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {user.phone}
                    </Typography>
                    {user.email && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {user.email}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {user.first_name || user.last_name
                        ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
                        : user.nickname || '-'}
                    </Typography>
                    {user.nickname && (user.first_name || user.last_name) && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        @{user.nickname}
                      </Typography>
                    )}
                    <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                      {user.is_superuser && <Chip label="Super" color="error" size="small" />}
                      {user.is_staff && <Chip label="Staff" color="primary" size="small" />}
                    </Box>
                  </TableCell>
                  <TableCell>
                    {user.is_banned ? (
                      <Chip label="Banned" color="error" size="small" />
                    ) : user.is_active ? (
                      <Chip label="Active" color="success" size="small" />
                    ) : (
                      <Chip label="Inactive" color="default" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    {user.subscription_plan ? (
                      <Chip 
                        label={user.subscription_plan.en || user.subscription_plan.ru || user.subscription_plan.tk || 'Unknown'} 
                        color="info" 
                        size="small" 
                      />
                    ) : (
                      <Chip label="None" color="default" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    {user.subscription_end_date ? (
                      <Box>
                        <Typography variant="body2" fontSize="0.8rem">
                          {formatDate(user.subscription_end_date)}
                        </Typography>
                        {new Date(user.subscription_end_date) < new Date() && (
                          <Chip label="Expired" color="error" size="small" sx={{ mt: 0.5 }} />
                        )}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    {userRequests.get(user.id) ? (
                      <Chip
                        label={userRequests.get(user.id)}
                        color="warning"
                        size="small"
                        onClick={() => handleViewUserRequests(user)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ) : (
                      <Typography variant="body2" color="text.secondary">-</Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Box display="flex" gap={0.5} justifyContent="flex-end">
                      <IconButton onClick={() => handleOpenDialog(user)} color="primary" size="small">
                        <Edit fontSize="small" />
                      </IconButton>
                      {user.subscription_plan ? (
                        <IconButton 
                          onClick={() => handleCancelSubscription(user)} 
                          color="warning"
                          size="small"
                          title="Cancel Subscription"
                        >
                          <Block fontSize="small" />
                        </IconButton>
                      ) : (
                        <IconButton 
                          onClick={() => handleOpenSubscriptionDialog(user)} 
                          color="success"
                          size="small"
                          title="Add Subscription"
                        >
                          <CheckCircle fontSize="small" />
                        </IconButton>
                      )}
                      <IconButton onClick={() => handleOpenDeleteDialog(user)} color="error" size="small">
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Edit/Create Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{editingUser ? t('editUser') : t('addUser')}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label={t('phone') + ' *'}
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            margin="dense"
            disabled={!!editingUser}
          />
          <TextField
            fullWidth
            label={t('email')}
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            margin="dense"
          />
          <TextField
            fullWidth
            label={t('firstName')}
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
            margin="dense"
          />
          <TextField
            fullWidth
            label={t('lastName')}
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            margin="dense"
          />

          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              {t('statusPermissions')}
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                />
              }
              label={t('active')}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_banned}
                  onChange={(e) => setFormData({ ...formData, is_banned: e.target.checked })}
                />
              }
              label={t('banned')}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_staff}
                  onChange={(e) => setFormData({ ...formData, is_staff: e.target.checked })}
                />
              }
              label={t('staff')}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={formData.is_superuser}
                  onChange={(e) => setFormData({ ...formData, is_superuser: e.target.checked })}
                />
              }
              label={t('superuser')}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>{t('cancel')}</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {editingUser ? t('update') : t('create')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>{t('confirmDelete')}</DialogTitle>
        <DialogContent>
          <Typography>
            {t('confirmDelete')} "{editingUser?.phone}"?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>{t('cancel')}</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            {t('delete')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Subscription Requests Dialog */}
      <Dialog 
        open={requestDialogOpen} 
        onClose={() => setRequestDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Subscription Requests - {editingUser?.first_name || editingUser?.last_name 
            ? `${editingUser?.first_name || ''} ${editingUser?.last_name || ''}`.trim()
            : editingUser?.phone}
        </DialogTitle>
        <DialogContent>
          {selectedUserRequests.length === 0 ? (
            <Typography>No pending requests</Typography>
          ) : (
            <Box sx={{ mt: 2 }}>
              {selectedUserRequests.map((request) => (
                <Paper key={request.id} sx={{ p: 2, mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box flex={1}>
                      <Typography variant="h6" gutterBottom>
                        {request.plan_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Period: {request.period === 'monthly' ? 'Monthly' : 'Yearly'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Amount: {request.amount} TMT
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Requested: {formatDate(request.created_at)}
                      </Typography>
                      {request.user_notes && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          Notes: {request.user_notes}
                        </Typography>
                      )}
                    </Box>
                    <Box display="flex" gap={1}>
                      <Button
                        variant="contained"
                        color="success"
                        size="small"
                        onClick={() => handleApproveRequest(request.id)}
                        startIcon={<CheckCircle />}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        onClick={() => handleRejectRequest(request.id)}
                        startIcon={<Block />}
                      >
                        Reject
                      </Button>
                    </Box>
                  </Box>
                </Paper>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Create Subscription Dialog */}
      <Dialog 
        open={subscriptionDialogOpen} 
        onClose={() => setSubscriptionDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingUser?.subscription_plan ? 'Manage' : 'Create'} Subscription - {editingUser?.first_name || editingUser?.last_name 
            ? `${editingUser?.first_name || ''} ${editingUser?.last_name || ''}`.trim()
            : editingUser?.phone}
        </DialogTitle>
        <DialogContent>
          {editingUser?.subscription_plan && (
            <Box sx={{ mb: 3, p: 2, bgcolor: '#e3f2fd', borderRadius: 1, border: '1px solid #2196f3' }}>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                <strong>Current Subscription:</strong>
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                Plan: {editingUser.subscription_plan.en || editingUser.subscription_plan.ru || editingUser.subscription_plan.tk}
              </Typography>
              <Typography variant="body2" sx={{ mb: 0.5 }}>
                Expires: {formatDate(editingUser.subscription_end_date)}
              </Typography>
              {editingUser.subscription_end_date && new Date(editingUser.subscription_end_date) < new Date() && (
                <Chip label="EXPIRED" color="error" size="small" sx={{ mt: 1 }} />
              )}
              <Button
                variant="outlined"
                color="error"
                size="small"
                fullWidth
                sx={{ mt: 2 }}
                onClick={() => {
                  setSubscriptionDialogOpen(false)
                  if (editingUser) {
                    handleCancelSubscription(editingUser)
                  }
                }}
                startIcon={<Block />}
              >
                Cancel Current Subscription
              </Button>
            </Box>
          )}
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {editingUser?.subscription_plan ? 'Create New Subscription (will replace current)' : 'Create New Subscription'}
            </Typography>
            <TextField
              select
              fullWidth
              label="Subscription Plan"
              value={subscriptionFormData.plan_id}
              onChange={(e) => setSubscriptionFormData({ 
                ...subscriptionFormData, 
                plan_id: e.target.value 
              })}
              margin="dense"
              required
            >
              {subscriptionPlans.map((plan) => (
                <MenuItem key={plan.id} value={plan.id}>
                  {plan.name.en || plan.name.ru || plan.name.tk} - {plan.monthly_price} {plan.currency}/month
                </MenuItem>
              ))}
            </TextField>

            <TextField
              fullWidth
              type="number"
              label="Duration (days)"
              value={subscriptionFormData.duration_days}
              onChange={(e) => setSubscriptionFormData({ 
                ...subscriptionFormData, 
                duration_days: parseInt(e.target.value) || 0
              })}
              margin="dense"
              required
              helperText="Enter number of days for subscription duration"
              inputProps={{ min: 1 }}
            />

            <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1, border: '1px solid #e0e0e0' }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                <strong>Quick Durations:</strong>
              </Typography>
              <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button 
                  size="small" 
                  variant="outlined"
                  color="primary"
                  onClick={() => setSubscriptionFormData({ ...subscriptionFormData, duration_days: 7 })}
                >
                  1 Week (7 days)
                </Button>
                <Button 
                  size="small" 
                  variant="outlined"
                  color="primary"
                  onClick={() => setSubscriptionFormData({ ...subscriptionFormData, duration_days: 30 })}
                >
                  1 Month (30 days)
                </Button>
                <Button 
                  size="small" 
                  variant="outlined"
                  color="primary"
                  onClick={() => setSubscriptionFormData({ ...subscriptionFormData, duration_days: 90 })}
                >
                  3 Months (90 days)
                </Button>
                <Button 
                  size="small" 
                  variant="outlined"
                  color="primary"
                  onClick={() => setSubscriptionFormData({ ...subscriptionFormData, duration_days: 365 })}
                >
                  1 Year (365 days)
                </Button>
              </Box>
            </Box>

            {subscriptionFormData.duration_days > 0 && (
              <Box sx={{ mt: 2, p: 2, bgcolor: '#e8f5e9', borderRadius: 1, border: '1px solid #4caf50' }}>
                <Typography variant="body2" sx={{ color: '#2e7d32' }}>
                  <strong>Subscription will be active for:</strong> {subscriptionFormData.duration_days} days
                  <br />
                  <strong>End date:</strong> {new Date(Date.now() + subscriptionFormData.duration_days * 24 * 60 * 60 * 1000).toLocaleDateString()}
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubscriptionDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateSubscription} 
            variant="contained" 
            color="success"
            disabled={!subscriptionFormData.plan_id || subscriptionFormData.duration_days <= 0}
          >
            Create Subscription
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
