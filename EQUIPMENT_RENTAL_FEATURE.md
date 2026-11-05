# Equipment Rental Feature

## Overview
Implemented equipment rental functionality for court bookings based on subscription plan features.

## Backend Changes

### 1. Models (`backend/apps/bookings/models.py`)
Added new fields to `Booking` model:
- `equipment_needed` (BooleanField) - Whether equipment is needed
- `equipment_details` (DictField) - Equipment details (e.g., {'rackets': 2, 'balls': 3})

### 2. Serializers (`backend/apps/bookings/serializers.py`)
Updated serializers to include equipment fields:
- `BookingSerializer` - Full booking details
- `BookingCreateSerializer` - Validates equipment logic
- `BookingListSerializer` - Minimal fields including equipment

**Validation Rules:**
- If `equipment_needed` is True, `equipment_details` must be provided
- Equipment quantities must be positive integers
- If `equipment_needed` is False, `equipment_details` is cleared

### 3. Views (`backend/apps/bookings/views.py`)
Enhanced `create` method in `BookingViewSet`:
- Checks if user has active subscription
- Validates if subscription plan includes `equipment_rental` feature
- Returns appropriate error if feature is not available

**Error Response Example:**
```json
{
  "error": "Equipment rental not available",
  "detail": "Your subscription plan does not include equipment rental",
  "feature": "equipment_rental"
}
```

## Mobile App Changes

### 1. Model (`mobile/lib/core/models/booking.dart`)
Added fields:
- `equipmentNeeded` (bool)
- `equipmentDetails` (Map<String, int>?)

### 2. Create Booking Screen (`mobile/lib/features/bookings/presentation/screens/create_booking_screen.dart`)
New screen with comprehensive booking form including:

**Features:**
- Date and time selection (DatePicker & TimePicker)
- Number of players counter
- Find opponents toggle with counter
- Equipment rental section:
  - Displays warning if plan doesn't include equipment rental
  - Toggle for equipment needed
  - Input fields for rackets and balls quantities
- Notes field
- Validation:
  - Date/time validation
  - End time must be after start time
  - Opponents validation
  - Equipment validation
- Real-time error display
- Success feedback with SnackBar

**Equipment Section Logic:**
1. Loads user's subscription plan on init
2. Checks if plan includes `equipment_rental` feature
3. If not included: Shows info message, disables equipment selection
4. If included: Shows toggle and quantity inputs
5. Validates quantities before submission

### 3. Court Detail Screen (`mobile/lib/features/courts/presentation/screens/court_detail_screen.dart`)
Fully implemented court details view:
- Court image display
- Court information (name, location, status, price)
- Description
- Category
- Amenities
- "Book Now" button (navigates to Create Booking Screen)
- Inactive court warning

### 4. Courts List Screen (`mobile/lib/features/courts/presentation/screens/courts_list_screen.dart`)
Implemented courts list with:
- Card-based layout
- Court images
- Court details (name, location, price, category)
- Status badges
- "Book Now" buttons
- Pull-to-refresh
- Navigation to court details

### 5. Localization (`mobile/lib/core/l10n/app_localizations.dart`)
Added translations for 3 languages (English, Russian, Turkmen):
- `create_booking` - Create Booking
- `date_and_time` - Date & Time
- `select_date` - Select Date
- `select_start_time` - Select Start Time
- `select_end_time` - Select End Time
- `equipment_rental` - Equipment Rental
- `need_equipment` - I need equipment
- `equipment_not_in_plan` - Equipment rental is not included in your subscription plan
- `select_equipment` - Select Equipment
- `rackets` - Rackets
- `balls` - Balls
- `please_specify_equipment` - Please specify equipment quantity
- `booking_created_successfully` - Booking created successfully!
- And more...

## API Flow

### Creating a Booking with Equipment

**Request:**
```http
POST /api/v1/bookings/
Authorization: Bearer <token>
Content-Type: application/json

{
  "court": "court-uuid",
  "start_time": "2025-12-25T10:00:00Z",
  "end_time": "2025-12-25T12:00:00Z",
  "number_of_players": 2,
  "find_opponents": false,
  "opponents_needed": 0,
  "equipment_needed": true,
  "equipment_details": {
    "rackets": 2,
    "balls": 3
  },
  "notes": "Optional notes"
}
```

**Success Response (201):**
```json
{
  "id": "booking-uuid",
  "court": "court-uuid",
  "start_time": "2025-12-25T10:00:00Z",
  "end_time": "2025-12-25T12:00:00Z",
  "status": "pending",
  "equipment_needed": true,
  "equipment_details": {
    "rackets": 2,
    "balls": 3
  },
  ...
}
```

**Error Response (403) - Feature Not Available:**
```json
{
  "error": "Equipment rental not available",
  "detail": "Your subscription plan does not include equipment rental",
  "feature": "equipment_rental"
}
```

## User Experience Flow

1. User navigates to Courts List
2. User selects a court
3. User views court details
4. User clicks "Book Now" button
5. Create Booking Screen opens
6. System loads user's subscription plan
7. If plan includes equipment rental:
   - Equipment section is enabled
   - User can toggle equipment needed
   - User can specify quantities
8. If plan doesn't include equipment rental:
   - Warning message is displayed
   - Equipment section is disabled
9. User fills in booking details
10. User submits booking
11. Backend validates:
    - Subscription status
    - Equipment rental feature
    - Time slot availability
    - Booking limits
12. Success: User sees confirmation, returns to previous screen
13. Error: User sees specific error message

## Testing Checklist

### Backend
- [ ] Create booking without equipment
- [ ] Create booking with equipment (plan includes feature)
- [ ] Create booking with equipment (plan doesn't include feature) - should fail
- [ ] Create booking with equipment_needed=true but empty equipment_details - should fail
- [ ] Create booking with invalid equipment quantities - should fail

### Mobile App
- [ ] Navigate to courts list
- [ ] View court details
- [ ] Open create booking screen
- [ ] Select date and time
- [ ] Test equipment section with plan that includes feature
- [ ] Test equipment section with plan that doesn't include feature
- [ ] Submit booking with equipment
- [ ] Submit booking without equipment
- [ ] Verify error messages display correctly
- [ ] Verify success message and navigation

## Future Enhancements
- Add more equipment types (shoes, uniforms, etc.)
- Add equipment availability checking
- Add equipment pricing
- Add equipment images
- Add equipment condition tracking
- Add equipment reservation history

