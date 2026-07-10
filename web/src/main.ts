import './styles.css'
import { api, session } from './api'
import { getLang, languages, setLang, t, type Lang } from './i18n'
import type { Booking, Category, Court, I18nText, Plan, Subscription, Tournament, User } from './types'

type RouteName =
  | 'home'
  | 'courts'
  | 'tournaments'
  | 'tariffs'
  | 'signin'
  | 'signup'
  | 'edit-profile'
  | 'settings'

interface State {
  user: User | null
  categories: Category[]
  courts: Court[]
  tournaments: Tournament[]
  plans: Plan[]
  loading: boolean
  error: string | null
  activeCourt: Court | null
  drawer: null | 'booking' | 'history' | 'my-tournaments' | 'subscription' | 'settings'
  profileMenuOpen: boolean
  search: string
  categoryId: string
  lang: Lang
}

const state: State = {
  user: session.user,
  categories: [],
  courts: [],
  tournaments: [],
  plans: [],
  loading: true,
  error: null,
  activeCourt: null,
  drawer: null,
  profileMenuOpen: false,
  search: '',
  categoryId: '',
  lang: getLang(),
}

const app = document.querySelector<HTMLDivElement>('#app')!

function route(): RouteName {
  const path = window.location.pathname.replace(/^\/+/, '') || 'home'
  if (['courts', 'tournaments', 'tariffs', 'signin', 'signup', 'edit-profile', 'settings'].includes(path)) {
    return path as RouteName
  }
  return 'home'
}

function navigate(path: string) {
  window.history.pushState({}, '', path)
  render()
}

function text(value: I18nText, fallback = ''): string {
  if (!value) return fallback
  if (typeof value === 'string') return value
  return value[state.lang] || value.ru || value.en || value.tk || Object.values(value)[0] || fallback
}

function tr(key: Parameters<typeof t>[1]) {
  return t(state.lang, key)
}

function money(value?: number, currency = 'TMT') {
  return `${Number(value || 0).toFixed(1)} ${currency}`
}

function date(value?: string) {
  if (!value) return ''
  return new Intl.DateTimeFormat(state.lang, { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(value))
}

function dateTime(value?: string) {
  if (!value) return ''
  return new Intl.DateTimeFormat(state.lang, {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function htmlEscape(value: string) {
  return value.replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  })[char] || char)
}

function firstImage(court: Court) {
  return court.images?.find(Boolean) || ''
}

function header(active: RouteName) {
  const userName = [state.user?.first_name, state.user?.last_name].filter(Boolean).join(' ') || state.user?.nickname || tr('profile')
  return `
    <header class="topbar">
      <button class="brand" data-link="/">
        <img src="/assets/app_logo.png" alt="Sportlink" />
      </button>
      <nav class="nav">
        ${navItem('/', tr('home'), active === 'home')}
        ${navItem('/tariffs', tr('tariffs'), active === 'tariffs')}
        ${navItem('/courts', tr('courts'), active === 'courts')}
        ${navItem('/tournaments', tr('tournaments'), active === 'tournaments')}
      </nav>
      <div class="top-actions">
        ${languageSelect('header')}
        ${state.user ? `
          <button class="profile-chip" data-action="profile-menu">
            <span class="user-icon">♡</span>
            <span>${htmlEscape(userName)}</span>
          </button>
        ` : `
          <button class="ghost-btn" data-link="/signin">${tr('signIn')}</button>
          <button class="orange-btn small" data-link="/signup">${tr('signUp')}</button>
        `}
      </div>
    </header>
  `
}

function languageSelect(scope: string) {
  return `
    <select class="lang-select" data-field="language" aria-label="${tr('language')}" data-scope="${scope}">
      ${Object.entries(languages).map(([code, label]) => `
        <option value="${code}" ${state.lang === code ? 'selected' : ''}>${label}</option>
      `).join('')}
    </select>
  `
}

function navItem(path: string, label: string, active: boolean) {
  return `<button class="nav-link ${active ? 'active' : ''}" data-link="${path}">${label}</button>`
}

function footer() {
  return `
    <footer class="footer">
      <div>
        <img class="footer-logo" src="/assets/app_logo.png" alt="Sportlink" />
        <p>${tr('footerTagline')}</p>
        <div class="store-row muted">
          <span class="store-badge">
            <img src="/assets/photos/appstoresymbol.png" alt="App Store" />
            <span class="store-text">
              <span>${tr('downloadedIn')}</span>
              <b>App Store</b>
            </span>
          </span>
          <span class="store-badge">
            <img src="/assets/photos/googleplaysymbol.png" alt="Google Play" />
            <span class="store-text">
              <span>${tr('availableIn')}</span>
              <b>Google Play</b>
            </span>
          </span>
        </div>
      </div>
      <div class="footer-cols">
        <div>
          <h4>${tr('navigation')}</h4>
          <button data-link="/">${tr('home')}</button>
          <button data-link="/courts">${tr('courts')}</button>
          <button data-link="/tournaments">${tr('tournaments')}</button>
          <button data-link="/tariffs">${tr('tariffs')}</button>
        </div>
        <div>
          <h4>${tr('documents')}</h4>
          <button data-doc="terms">${tr('terms')}</button>
          <button data-doc="privacy">${tr('privacy')}</button>
        </div>
      </div>
    </footer>
  `
}

function filterBar(kind: 'courts' | 'tournaments') {
  const options = state.categories.map((category) => `
    <option value="${category.id}" ${state.categoryId === category.id ? 'selected' : ''}>${htmlEscape(text(category.name_i18n, tr('sport')))}</option>
  `).join('')
  return `
    <div class="filters">
      <select class="sport-select" data-field="category">
        <option value="">${kind === 'courts' ? tr('allSports') : tr('allTournaments')}</option>
        ${options}
      </select>
      <label class="search">
        <span>⌕</span>
        <input data-field="search" type="search" value="${htmlEscape(state.search)}" placeholder="${tr('search')}" />
      </label>
    </div>
  `
}

function courtCard(court: Court) {
  const name = text(court.name_i18n, tr('court'))
  const image = firstImage(court)
  return `
    <article class="card court-card">
      ${image ? `<img src="${image}" alt="${htmlEscape(name)}" />` : `<div class="image-placeholder">${tr('noPhoto')}</div>`}
      <div class="card-body">
        <h3>${htmlEscape(name)}</h3>
        <p class="location">● ${htmlEscape(court.address || '')}</p>
        <button class="orange-btn full" data-book="${court.id}">${tr('book')}</button>
      </div>
    </article>
  `
}

function tournamentCard(tournament: Tournament) {
  const name = text(tournament.name_i18n, tr('tournaments'))
  const description = text(tournament.description_i18n, '')
  const place = tournament.location_description || [tournament.city, tournament.country].filter(Boolean).join(', ')
  const status = tournament.registration_open ? tr('registrationOpen') : (tournament.status || tr('registrationClosed'))
  return `
    <article class="card tournament-card">
      <div class="card-media">
        ${tournament.image_url ? `<img src="${tournament.image_url}" alt="${htmlEscape(name)}" />` : `<div class="image-placeholder">${tr('noPhoto')}</div>`}
        <span class="status-pill">${htmlEscape(status)}</span>
      </div>
      <div class="card-body">
        <h3>${htmlEscape(name)}</h3>
        <p>${htmlEscape(description)}</p>
        <ul class="meta-list">
          <li>□ ${date(tournament.start_date)} - ${date(tournament.end_date)}</li>
          <li>● ${htmlEscape(place)}</li>
          <li>♧ ${tournament.participant_count || 0}/${tournament.max_participants || 0} ${tr('participants')}</li>
          <li>$ ${tr('registrationFee')}: ${money(tournament.registration_fee)}</li>
          <li>◷ ${tr('registerUntil')}: ${date(tournament.registration_deadline)}</li>
        </ul>
        <button class="orange-btn full" data-register-tournament="${tournament.id}">${tr('details')}</button>
      </div>
    </article>
  `
}

function emptyState(title: string) {
  return `<div class="empty-state">${htmlEscape(title)}</div>`
}

function grid(items: string[], emptyText: string) {
  if (state.loading) return `<div class="grid">${Array.from({ length: 8 }, () => '<div class="skeleton"></div>').join('')}</div>`
  if (state.error) return `<div class="empty-state error">${htmlEscape(state.error)}</div>`
  if (!items.length) return emptyState(emptyText)
  return `<div class="grid">${items.join('')}</div>`
}

function homePage() {
  if (state.user) {
    return `
      ${header('home')}
      <main class="page shell">
        ${filterBar('courts')}
        ${grid(filteredCourts().map(courtCard), tr('noCourts'))}
      </main>
      ${footer()}
      ${profileMenu()}
      ${drawer()}
    `
  }

  const courtCards = state.courts.slice(0, 4).map(courtCard)
  const tournamentCards = state.tournaments.slice(0, 4).map(tournamentCard)
  return `
    ${header('home')}
    <main>
      <section class="hero shell">
        <div class="hero-copy">
          <div class="eyebrow"><span>${tr('quickStart')}</span> <b>${state.courts.length || 0} ${tr('onlineCourts')}</b></div>
          <h1>${tr('heroTitleA')}<br><span>${tr('heroTitleB')}</span></h1>
          <p>${tr('heroText')}</p>
          <div class="hero-actions">
            <button class="orange-btn hero-btn" data-link="/signup">${tr('signUp')}</button>
            <div class="store-row">
              <span class="divider"></span>
              <span class="store-label">${tr('appAlways')}</span>
              <span class="store-dark hero-store">
                <img src="/assets/photos/appstoresymbol.png" alt="App Store" />
                <span class="store-text">
                  <span>${tr('downloadedIn')}</span>
                  <b>App Store</b>
                </span>
              </span>
              <span class="store-dark hero-store">
                <img src="/assets/photos/googleplaysymbol.png" alt="Google Play" />
                <span class="store-text">
                  <span>${tr('availableIn')}</span>
                  <b>Google Play</b>
                </span>
              </span>
            </div>
          </div>
          <small>${tr('firstGameBonus')}</small>
          <div class="stats">
            <div><b>${state.courts.length || 0}+</b><span>${tr('courtsInSystem')}</span></div>
            <div><b>${state.tournaments.length || 0}+</b><span>${tr('tournamentsOnline')}</span></div>
            <div><b>${state.plans.length || 0}</b><span>${tr('plansAvailable')}</span></div>
          </div>
        </div>
        <div class="hero-phone">
          <img
            src="/assets/photos/RIGHT%20SIDE_%20Responsive%20Interactive%20Smartphone%20Mockup%20with%20Simulated%20Booking.png"
            alt="Sportlink app screenshot"
          />
        </div>
      </section>
      <section class="shell section">
        <h2>${tr('courts')}</h2>
        ${grid(courtCards, tr('noCourts'))}
      </section>
      <section class="shell section">
        <h2>${tr('tournaments')}</h2>
        ${grid(tournamentCards, tr('noTournaments'))}
      </section>
    </main>
    ${footer()}
  `
}

function listingPage(kind: 'courts' | 'tournaments') {
  return `
    ${header(kind)}
    <main class="page shell">
      ${filterBar(kind)}
      ${kind === 'courts'
        ? grid(filteredCourts().map(courtCard), tr('noCourts'))
        : grid(filteredTournaments().map(tournamentCard), tr('noTournaments'))}
    </main>
    ${footer()}
    ${profileMenu()}
    ${drawer()}
  `
}

function tariffsPage() {
  const cards = state.plans
    .slice()
    .sort((a, b) => (a.order || 0) - (b.order || 0))
    .map(planCard)
  return `
    ${header('tariffs')}
    <main class="tariff-page shell">
      ${grid(cards, tr('noPlans'))}
    </main>
    ${footer()}
    ${profileMenu()}
    ${drawer()}
  `
}

function planCard(plan: Plan) {
  const features = Object.entries(plan.features || {}).filter(([, enabled]) => enabled).map(([key]) => featureLabel(key))
  const limits = plan.booking_limits || {}
  return `
    <article class="plan-card ${plan.is_popular ? 'popular' : ''}">
      <div class="plan-head">
        <h2>${htmlEscape(text(plan.name, tr('tariffs')))}</h2>
        ${plan.is_popular ? `<span class="popular-pill">${tr('popular')}</span>` : ''}
        ${(plan.discount_percentage || 0) > 0 ? `<span class="discount-pill">-${plan.discount_percentage}%</span>` : ''}
      </div>
      <p>${htmlEscape(text(plan.description, ''))}</p>
      <div class="price">
        <b>${money(plan.monthly_price, plan.currency)}</b>
        <span>/${tr('month')}</span>
      </div>
      <ul class="feature-list">
        ${features.map((feature) => `<li>✓ ${htmlEscape(feature)}</li>`).join('')}
      </ul>
      <div class="limits">
        <b>${tr('bookingLimits')}</b>
        <span>• ${limits.bookings_per_week || 0} ${tr('bookingsPerWeek')}</span>
        <span>• ${tr('maxHours')}: ${limits.max_duration_hours || 0}</span>
        <span>• ${tr('days')}: ${formatDays(limits.allowed_days)}</span>
      </div>
      <button class="orange-btn full" data-subscribe="${plan.id}">${tr('apply')}</button>
    </article>
  `
}

function authPage(mode: 'signin' | 'signup') {
  return `
    <main class="auth-page">
      <button class="auth-logo" data-link="/"><img src="/assets/app_logo.png" alt="Sportlink"></button>
      <form class="auth-form" data-form="${mode}">
        ${mode === 'signup' ? `
          <div class="two-cols">
            ${input('first_name', tr('firstName'), 'Michael')}
            ${input('last_name', tr('lastName'), 'Jordan')}
          </div>
          ${input('nickname', tr('nickname'), 'Jordan')}
        ` : ''}
        ${input(mode === 'signin' ? 'identifier' : 'phone', mode === 'signin' ? '' : tr('phone'), '+993 xx xxxxxx')}
        ${input('password', mode === 'signin' ? '' : tr('password'), tr('password'), 'password')}
        ${mode === 'signup' ? input('confirm_password', tr('confirmPassword'), '***********', 'password') : ''}
        <button class="orange-btn auth-submit" type="submit">${mode === 'signup' ? tr('signUp') : tr('signIn')}</button>
        <p class="auth-switch">
          ${mode === 'signup'
            ? `${tr('haveAccount')} <button type="button" data-link="/signin">${tr('signIn')}</button>`
            : `${tr('noAccount')} <button type="button" data-link="/signup">${tr('createAccount')}</button>`}
        </p>
      </form>
    </main>
  `
}

function input(name: string, label: string, placeholder: string, type = 'text', value = '') {
  return `
    <label class="field">
      ${label ? `<span>${label}</span>` : ''}
      <input name="${name}" type="${type}" placeholder="${placeholder}" value="${htmlEscape(value)}" />
    </label>
  `
}

function editProfilePage() {
  const user = state.user
  if (!user) return authPage('signin')
  return `
    ${header('home')}
    <main class="profile-edit shell">
      <form data-form="profile">
        <div class="profile-grid">
          <div>
            ${input('first_name', tr('firstName'), tr('firstName'), 'text', user.first_name || '')}
            ${input('last_name', tr('lastName'), tr('lastName'), 'text', user.last_name || '')}
            ${input('email', 'E-mail', 'example@mail.com', 'email', user.email || '')}
            ${input('city', tr('city'), tr('ashgabat'), 'text', user.city || '')}
          </div>
          <div>
            ${input('age', tr('age'), '24', 'number', user.age ? String(user.age) : '')}
            ${input('gender', tr('gender'), tr('gender'), 'text', user.gender || '')}
            <h3>${tr('accountInfo')}</h3>
            ${lockedInput(tr('phone'), user.phone || '')}
            ${lockedInput(tr('nickname'), user.nickname || '')}
          </div>
        </div>
        <hr>
        <section class="favorite-sports">
          <h3>${tr('favoriteSports')}</h3>
          ${favoriteSports()}
        </section>
        <div class="form-actions">
          <button class="outline-btn" type="button" data-link="/">${tr('cancel')}</button>
          <button class="orange-btn" type="submit">${tr('save')}</button>
        </div>
      </form>
    </main>
    ${footer()}
    ${profileMenu()}
  `
}

function lockedInput(label: string, value: string) {
  return `
    <label class="field locked">
      <span>${label}</span>
      <input value="${htmlEscape(value)}" disabled />
      <b>▣</b>
    </label>
  `
}

function favoriteSports() {
  const sports = state.user?.favorite_sports || []
  return `
    <div class="sport-box">
      ${sports.length ? sports.map((sport) => `
        <b>${htmlEscape(text(sport.category_name, tr('sport')))}</b>
        <span>Experience level: ${sport.experience_level}/10</span>
        <progress value="${sport.experience_level}" max="10"></progress>
      `).join('') : `<span>${tr('noFavoriteSports')}</span>`}
    </div>
    <button class="outline-btn add-sport" type="button">${tr('add')}</button>
  `
}

function settingsPage() {
  if (!state.user) return authPage('signin')
  return `
    ${header('home')}
    <main class="page shell">
      <section class="center-panel settings-panel">
        <h1>${tr('settings')}</h1>
        <div class="setting-group">
          <label>${tr('language')}</label>
          ${languageSelect('settings')}
        </div>
        <div class="setting-group">
          <label>${tr('account')}</label>
          <button data-action="change-password">${tr('changePassword')} <span>›</span></button>
          <button data-doc="privacy">${tr('privacy')} <span>›</span></button>
          <button data-doc="terms">${tr('terms')} <span>›</span></button>
        </div>
      </section>
    </main>
    ${footer()}
    ${profileMenu()}
  `
}

function profileMenu() {
  if (!state.user || !state.profileMenuOpen) return ''
  const subscription = state.user.subscription
  return `
    <div class="profile-menu">
      <label class="menu-toggle">
        <span>${tr('findOpponents')}</span>
        <small>${tr('setSchedule')}</small>
        <input type="checkbox" ${state.user.available_for_opponent_search ? 'checked' : ''} data-action="toggle-opponents">
      </label>
      <button data-drawer="subscription">${tr('subscription')} ${subscription ? `<b>Active: ${htmlEscape(text(subscription.plan_name, tr('plan')))}</b>` : ''}</button>
      <button data-link="/edit-profile">${tr('editProfile')} <span>›</span></button>
      <button data-drawer="history">${tr('bookingHistory')} <span>›</span></button>
      <button data-drawer="my-tournaments">${tr('myTournaments')} <span>›</span></button>
      <button data-drawer="settings">${tr('settings')} <span>›</span></button>
      <button class="logout" data-action="logout">${tr('logout')}</button>
    </div>
  `
}

function drawer() {
  if (!state.drawer) return ''
  const title = {
    booking: '',
    history: tr('bookingHistory'),
    'my-tournaments': tr('myTournaments'),
    subscription: tr('subscription'),
    settings: tr('settings'),
  }[state.drawer]
  return `
    <div class="shade" data-action="close-drawer"></div>
    <aside class="side-drawer">
      <button class="drawer-close" data-action="close-drawer">×</button>
      ${title ? `<h1>${title}</h1>` : ''}
      <div data-drawer-content>${drawerContent()}</div>
    </aside>
  `
}

function drawerContent() {
  if (state.drawer === 'booking' && state.activeCourt) return bookingForm(state.activeCourt)
  if (state.drawer === 'history') return asyncPanel('bookings')
  if (state.drawer === 'my-tournaments') return asyncPanel('registrations')
  if (state.drawer === 'subscription') return subscriptionPanel()
  if (state.drawer === 'settings') return settingsDrawer()
  return ''
}

function bookingForm(court: Court) {
  return `
    <section class="booking-form">
      <h1>${htmlEscape(text(court.name_i18n, tr('court')))}</h1>
      <p class="location">● ${htmlEscape(court.address || '')}</p>
      <form data-form="booking">
        ${input('date', tr('date'), '', 'date')}
        <div class="two-cols">
          ${input('start', tr('startTime'), '', 'time')}
          ${input('end', tr('endTime'), '', 'time')}
        </div>
        <button class="outline-btn full" type="button" data-action="check-availability">${tr('checkAvailability')}</button>
        <div class="option-row">
          <span>${tr('groupPlayers')}</span>
          <input name="number_of_players" type="number" min="1" value="1">
        </div>
        <label class="option-row">
          <span>${tr('findOpponents')}</span>
          <input name="find_opponents" type="checkbox">
        </label>
        <div class="option-row nested">
          <span>${tr('opponentsNeeded')}</span>
          <input name="opponents_needed" type="number" min="0" value="0">
        </div>
        <label class="option-row">
          <span>${tr('equipmentRental')}</span>
          <input name="equipment_needed" type="checkbox">
        </label>
        <textarea name="notes" placeholder="${tr('notes')}"></textarea>
        <button class="orange-btn full" type="submit">${tr('confirmBooking')}</button>
      </form>
    </section>
  `
}

function asyncPanel(kind: 'bookings' | 'registrations') {
  return `<div class="panel-list" data-async-panel="${kind}"><div class="mini-loader">${tr('loading')}</div></div>`
}

function subscriptionPanel() {
  const subscription = state.user?.subscription
  if (!subscription) return emptyState(tr('noSubscription'))
  const features = Object.entries(subscription.plan_features || {}).filter(([, enabled]) => enabled).map(([key]) => featureLabel(key))
  const daysLeft = subscription.end_date ? Math.max(0, Math.ceil((new Date(subscription.end_date).getTime() - Date.now()) / 86400000)) : 0
  return `
    <article class="my-subscription">
      <span class="active-pill">${htmlEscape(subscription.status || 'Active')}</span>
      <h2>${htmlEscape(text(subscription.plan_name, tr('subscription')))}</h2>
      <p>${tr('expires')}: ${date(subscription.end_date)}</p>
      <p>${tr('daysLeft')}: ${daysLeft}</p>
      <hr>
      <ul class="feature-list">${features.map((feature) => `<li>✓ ${htmlEscape(feature)}</li>`).join('')}</ul>
    </article>
  `
}

function settingsDrawer() {
  return `
    <div class="setting-group">
      <label>${tr('language')}</label>
      ${languageSelect('drawer')}
    </div>
    <div class="setting-group">
      <label>${tr('account')}</label>
      <button data-action="change-password">${tr('changePassword')} <span>›</span></button>
      <button data-doc="privacy">${tr('privacy')} <span>›</span></button>
      <button data-doc="terms">${tr('terms')} <span>›</span></button>
    </div>
  `
}

function filteredCourts() {
  const search = state.search.trim().toLowerCase()
  return state.courts.filter((court) => {
    const matchesCategory = !state.categoryId || court.type === state.categoryId || court.category_info?.id === state.categoryId
    const haystack = `${text(court.name_i18n)} ${court.address || ''}`.toLowerCase()
    return matchesCategory && (!search || haystack.includes(search))
  })
}

function filteredTournaments() {
  const search = state.search.trim().toLowerCase()
  return state.tournaments.filter((tournament) => {
    const haystack = `${text(tournament.name_i18n)} ${text(tournament.description_i18n)} ${tournament.city || ''}`.toLowerCase()
    const matchesCategory = !state.categoryId || tournament.categories?.includes(state.categoryId)
    return matchesCategory && (!search || haystack.includes(search))
  })
}

function featureLabel(key: string) {
  const labels: Record<string, string> = {
    court_booking: tr('courtBooking'),
    opponent_matching: tr('opponentMatching'),
    tournament_registration: tr('tournamentRegistration'),
    rental_discount: tr('rentalDiscount'),
    weekend_booking: tr('weekendBooking'),
    equipment_rental: tr('equipmentRental'),
    extended_statistics: tr('extendedStatistics'),
  }
  return labels[key] || key.replace(/_/g, ' ')
}

function formatDays(value: unknown) {
  const names = {
    ru: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
    en: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    tk: ['Duş', 'Siş', 'Çar', 'Pen', 'Ann', 'Şen', 'Ýek'],
  }[state.lang]
  if (!Array.isArray(value) || value.length === 0) return tr('allDays')
  return value.map((day) => names[Number(day) - 1]).filter(Boolean).join(', ')
}

function render() {
  const current = route()
  state.profileMenuOpen = current === 'edit-profile' ? false : state.profileMenuOpen
  if (current === 'signin') app.innerHTML = authPage('signin')
  else if (current === 'signup') app.innerHTML = authPage('signup')
  else if (current === 'courts') app.innerHTML = listingPage('courts')
  else if (current === 'tournaments') app.innerHTML = listingPage('tournaments')
  else if (current === 'tariffs') app.innerHTML = tariffsPage()
  else if (current === 'edit-profile') app.innerHTML = editProfilePage()
  else if (current === 'settings') app.innerHTML = settingsPage()
  else app.innerHTML = homePage()
  bindAsyncPanels()
}

async function loadData() {
  state.loading = true
  render()
  try {
    const [categories, courts, tournaments, plans] = await Promise.all([
      api.categories(),
      api.courts(),
      api.tournaments(),
      api.plans(),
    ])
    state.categories = categories
    state.courts = courts
    state.tournaments = tournaments
    state.plans = plans
    if (session.token) state.user = await api.me().catch(() => session.user)
    state.error = null
  } catch (error) {
    state.error = error instanceof Error ? error.message : tr('loadFailed')
  } finally {
    state.loading = false
    render()
  }
}

function bindAsyncPanels() {
  document.querySelectorAll<HTMLElement>('[data-async-panel]').forEach(async (node) => {
    const kind = node.dataset.asyncPanel
    try {
      if (kind === 'bookings') {
        const bookings = await api.myBookings()
        node.innerHTML = bookings.length ? bookings.map(bookingItem).join('') : emptyState(tr('emptyBookings'))
      }
      if (kind === 'registrations') {
        const tournaments = await api.myRegistrations()
        node.innerHTML = tournaments.length ? tournaments.map(myTournamentItem).join('') : emptyState(tr('emptyMyTournaments'))
      }
    } catch (error) {
      node.innerHTML = `<div class="empty-state error">${htmlEscape(error instanceof Error ? error.message : tr('errorLoading'))}</div>`
    }
  })
}

function bookingItem(booking: Booking) {
  return `
    <article class="booking-item">
      <div class="booking-icon">⚽</div>
      <div>
        <b>${htmlEscape(booking.court_name || text(booking.court_details?.name_i18n, tr('court')))}</b>
        <span>${dateTime(booking.start_time)} - ${booking.end_time ? new Date(booking.end_time).toLocaleTimeString(state.lang, { hour: '2-digit', minute: '2-digit' }) : ''}</span>
      </div>
      <em>${htmlEscape(booking.status || '')}</em>
    </article>
  `
}

function myTournamentItem(tournament: Tournament) {
  return `
    <article class="booking-item">
      <div class="booking-icon">🏆</div>
      <div>
        <b>${htmlEscape(text(tournament.name_i18n, tr('tournaments')))}</b>
        <span>${date(tournament.start_date)} - ${date(tournament.end_date)}</span>
      </div>
      <em>${htmlEscape(tournament.status || '')}</em>
    </article>
  `
}

app.addEventListener('click', async (event) => {
  const target = event.target as HTMLElement
  const link = target.closest<HTMLElement>('[data-link]')
  if (link) {
    event.preventDefault()
    navigate(link.dataset.link || '/')
    return
  }

  const action = target.closest<HTMLElement>('[data-action]')?.dataset.action
  if (action === 'profile-menu') {
    state.profileMenuOpen = !state.profileMenuOpen
    render()
  }
  if (action === 'logout') {
    session.clear()
    state.user = null
    state.profileMenuOpen = false
    navigate('/')
  }
  if (action === 'close-drawer') {
    state.drawer = null
    state.activeCourt = null
    render()
  }

  const drawerTrigger = target.closest<HTMLElement>('[data-drawer]')
  if (drawerTrigger) {
    state.drawer = drawerTrigger.dataset.drawer as State['drawer']
    state.profileMenuOpen = false
    render()
  }

  const book = target.closest<HTMLElement>('[data-book]')
  if (book) {
    if (!state.user) {
      navigate('/signin')
      return
    }
    state.activeCourt = state.courts.find((court) => court.id === book.dataset.book) || null
    state.drawer = 'booking'
    render()
  }

  const subscribe = target.closest<HTMLElement>('[data-subscribe]')
  if (subscribe) {
    if (!state.user) {
      navigate('/signin')
      return
    }
    await runAction(() => api.subscribe(subscribe.dataset.subscribe || ''), tr('subscriptionSent'))
  }

  const tournament = target.closest<HTMLElement>('[data-register-tournament]')
  if (tournament) {
    if (!state.user) {
      navigate('/signin')
      return
    }
    await runAction(() => api.registerTournament(tournament.dataset.registerTournament || ''), tr('tournamentSent'))
  }

  if (action === 'check-availability') {
    await checkAvailability()
  }
})

app.addEventListener('input', (event) => {
  const target = event.target as HTMLInputElement | HTMLSelectElement
  if (target.dataset.field === 'search') {
    state.search = target.value
    render()
  }
  if (target.dataset.field === 'category') {
    state.categoryId = target.value
    render()
  }
  if (target.dataset.field === 'language') {
    state.lang = target.value as Lang
    setLang(state.lang)
    render()
  }
})

app.addEventListener('submit', async (event) => {
  event.preventDefault()
  const form = event.target as HTMLFormElement
  const type = form.dataset.form
  const formData = Object.fromEntries(new FormData(form).entries())
  try {
    if (type === 'signin') {
      await api.login(String(formData.identifier), String(formData.password))
      state.user = session.user
      navigate('/')
    }
    if (type === 'signup') {
      if (formData.password !== formData.confirm_password) throw new Error(tr('passwordsMismatch'))
      await api.register({
        first_name: String(formData.first_name),
        last_name: String(formData.last_name),
        nickname: String(formData.nickname),
        phone: String(formData.phone),
        password: String(formData.password),
      })
      state.user = session.user
      navigate('/')
    }
    if (type === 'profile') {
      state.user = await api.updateMe({
        first_name: String(formData.first_name),
        last_name: String(formData.last_name),
        email: String(formData.email),
        city: String(formData.city),
        age: formData.age ? Number(formData.age) : undefined,
        gender: String(formData.gender),
      })
      navigate('/')
    }
    if (type === 'booking') {
      await createBooking(formData)
    }
  } catch (error) {
    alert(error instanceof Error ? error.message : tr('error'))
  }
})

async function checkAvailability() {
  const form = document.querySelector<HTMLFormElement>('[data-form="booking"]')
  if (!form || !state.activeCourt) return
  const data = Object.fromEntries(new FormData(form).entries())
  const start_time = toIso(String(data.date), String(data.start))
  const end_time = toIso(String(data.date), String(data.end))
  if (!start_time || !end_time) {
    alert(tr('chooseDateTime'))
    return
  }
  await runAction(() => api.checkAvailability({ court_id: state.activeCourt!.id, start_time, end_time }), tr('timeAvailable'))
}

async function createBooking(formData: Record<string, FormDataEntryValue>) {
  if (!state.activeCourt) return
  const start_time = toIso(String(formData.date), String(formData.start))
  const end_time = toIso(String(formData.date), String(formData.end))
  if (!start_time || !end_time) throw new Error(tr('chooseDateTime'))
  await api.createBooking({
    court: state.activeCourt.id,
    start_time,
    end_time,
    number_of_players: Number(formData.number_of_players || 1),
    find_opponents: Boolean(formData.find_opponents),
    opponents_needed: Number(formData.opponents_needed || 0),
    equipment_needed: Boolean(formData.equipment_needed),
    equipment_details: {},
    notes: String(formData.notes || ''),
  })
  state.drawer = null
  state.activeCourt = null
  alert(tr('bookingCreated'))
  render()
}

function toIso(datePart: string, timePart: string) {
  if (!datePart || !timePart) return ''
  return new Date(`${datePart}T${timePart}:00`).toISOString()
}

async function runAction(action: () => Promise<unknown>, success: string) {
  try {
    await action()
    alert(success)
    if (session.token) state.user = await api.me().catch(() => state.user)
    render()
  } catch (error) {
    alert(error instanceof Error ? error.message : tr('error'))
  }
}

window.addEventListener('popstate', render)
loadData()
