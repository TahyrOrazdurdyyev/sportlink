import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Paper,
  Grid,
} from '@mui/material'

interface WorkingHours {
  day_of_week: number
  is_working_day: boolean
  start_time: string
  end_time: string
}

interface WorkingHoursEditorProps {
  workingHours: WorkingHours[]
  onChange: (workingHours: WorkingHours[]) => void
}

const DAYS_OF_WEEK = [
  { value: 0, key: 'monday' },
  { value: 1, key: 'tuesday' },
  { value: 2, key: 'wednesday' },
  { value: 3, key: 'thursday' },
  { value: 4, key: 'friday' },
  { value: 5, key: 'saturday' },
  { value: 6, key: 'sunday' },
]

export function WorkingHoursEditor({ workingHours, onChange }: WorkingHoursEditorProps) {
  const { t } = useTranslation()

  // Initialize with all days if empty
  const [schedule, setSchedule] = useState<WorkingHours[]>(() => {
    if (workingHours && workingHours.length > 0) {
      return workingHours
    }
    // Default: all days 09:00-22:00
    return DAYS_OF_WEEK.map(day => ({
      day_of_week: day.value,
      is_working_day: true,
      start_time: '09:00',
      end_time: '22:00',
    }))
  })

  const handleDayToggle = (dayIndex: number) => {
    const newSchedule = [...schedule]
    const day = newSchedule.find(d => d.day_of_week === dayIndex)
    if (day) {
      day.is_working_day = !day.is_working_day
    }
    setSchedule(newSchedule)
    onChange(newSchedule)
  }

  const handleTimeChange = (dayIndex: number, field: 'start_time' | 'end_time', value: string) => {
    const newSchedule = [...schedule]
    const day = newSchedule.find(d => d.day_of_week === dayIndex)
    if (day) {
      day[field] = value
    }
    setSchedule(newSchedule)
    onChange(newSchedule)
  }

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom fontWeight="bold" sx={{ mb: 2 }}>
        {t('workingHours')}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {t('workingHoursDescription')}
      </Typography>

      {DAYS_OF_WEEK.map((day) => {
        const daySchedule = schedule.find(s => s.day_of_week === day.value) || {
          day_of_week: day.value,
          is_working_day: true,
          start_time: '09:00',
          end_time: '22:00',
        }

        return (
          <Paper key={day.value} variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={3}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={daySchedule.is_working_day}
                      onChange={() => handleDayToggle(day.value)}
                    />
                  }
                  label={t(day.key)}
                />
              </Grid>
              {daySchedule.is_working_day && (
                <>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      type="time"
                      label={t('startTime')}
                      value={daySchedule.start_time}
                      onChange={(e) => handleTimeChange(day.value, 'start_time', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      type="time"
                      label={t('endTime')}
                      value={daySchedule.end_time}
                      onChange={(e) => handleTimeChange(day.value, 'end_time', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      size="small"
                    />
                  </Grid>
                </>
              )}
            </Grid>
          </Paper>
        )
      })}
    </Box>
  )
}

