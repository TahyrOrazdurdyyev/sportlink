(() => {
  const mockupSrc = '/assets/photos/RIGHT%20SIDE_%20Responsive%20Interactive%20Smartphone%20Mockup%20with%20Simulated%20Booking.png'
  const translations = {
    ru: {
      android: 'Скачать на Android',
      iphone: 'Скачать на iPhone',
      title: 'Установка Sportlink на iPhone',
      intro: 'Добавьте Sportlink на главный экран iPhone — приложение откроется отдельно, как обычное приложение.',
      steps: [
        'Откройте sportlink.com.tm в браузере Safari.',
        'Нажмите кнопку «Поделиться» в нижней части экрана.',
        'Выберите «На экран Домой». При необходимости прокрутите список действий вниз.',
        'Нажмите «Добавить» в правом верхнем углу.',
      ],
      note: 'После этого значок Sportlink появится на главном экране. Открывайте сайт через этот значок.',
      back: 'Вернуться на главную',
    },
    en: {
      android: 'Download for Android',
      iphone: 'Get it on iPhone',
      title: 'Install Sportlink on iPhone',
      intro: 'Add Sportlink to your iPhone Home Screen. It will open separately, like a regular app.',
      steps: [
        'Open sportlink.com.tm in the Safari browser.',
        'Tap the Share button at the bottom of the screen.',
        'Choose “Add to Home Screen”. Scroll down the actions if needed.',
        'Tap “Add” in the top-right corner.',
      ],
      note: 'The Sportlink icon will appear on your Home Screen. Open the site using that icon.',
      back: 'Back to home',
    },
    tk: {
      android: 'Android üçin ýükläň',
      iphone: 'iPhone üçin goşuň',
      title: 'Sportlink-i iPhone-a gurnamak',
      intro: 'Sportlink-i iPhone-yň baş ekranyna goşuň. Ol adaty programma ýaly aýratyn açylar.',
      steps: [
        'Safari brauzerinde sportlink.com.tm sahypasyny açyň.',
        'Ekranyň aşagyndaky «Paýlaş» düwmesine basyň.',
        '«Baş ekrana goş» saýlaň. Gerek bolsa, hereketleriň sanawyny aşak süýşüriň.',
        'Ýokarky sag burçdaky «Goş» düwmesine basyň.',
      ],
      note: 'Sportlink nyşany baş ekranda peýda bolar. Saýty şol nyşan arkaly açyň.',
      back: 'Baş sahypa dolanmak',
    },
  }

  let iosPage = false

  const nativeFetch = window.fetch.bind(window)
  let refreshInProgress = null
  let activeBookingCourtId = null
  let equipmentLoadId = null

  async function refreshAccessToken() {
    if (refreshInProgress) return refreshInProgress
    const refreshToken = localStorage.getItem('sportlink_web_refresh')
    if (!refreshToken) return null

    refreshInProgress = nativeFetch('/api/v1/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ refresh: refreshToken }),
    }).then(async (response) => {
      if (!response.ok) return null
      const payload = await response.json()
      if (typeof payload.access !== 'string' || !payload.access) return null
      localStorage.setItem('sportlink_web_access', payload.access)
      return payload.access
    }).catch((error) => {
      console.error('Failed to refresh the Sportlink access token.', error)
      return null
    }).finally(() => {
      refreshInProgress = null
    })
    return refreshInProgress
  }

  function formatApiError(value) {
    if (typeof value === 'string') return value
    if (typeof value === 'number' || typeof value === 'boolean') return String(value)
    if (Array.isArray(value)) return value.map(formatApiError).filter(Boolean).join('; ')
    if (value && typeof value === 'object') {
      return Object.entries(value)
        .map(([key, detail]) => {
          const formatted = formatApiError(detail)
          return formatted ? `${key}: ${formatted}` : ''
        })
        .filter(Boolean)
        .join('; ')
    }
    return ''
  }

  window.fetch = async (input, init) => {
    const requestUrl = input instanceof Request ? input.url : String(input)
    const requestPath = new URL(requestUrl, location.href).pathname
    const method = (init?.method || (input instanceof Request ? input.method : 'GET')).toUpperCase()
    let requestInit = init
    if (method === 'POST' && /\/subscriptions\/requests\/create\/?$/.test(requestPath) && typeof init?.body === 'string') {
      try {
        const payload = JSON.parse(init.body)
        if (!payload.period) {
          requestInit = { ...requestInit, body: JSON.stringify({ ...payload, period: 'monthly' }) }
        }
      } catch (error) {
        console.error('Could not add a subscription period to the request.', error)
      }
    }

    if (method === 'POST' && /\/bookings\/?$/.test(requestPath) && typeof requestInit?.body === 'string') {
      try {
        const payload = JSON.parse(requestInit.body)
        if (payload.equipment_needed) {
          const details = {}
          document.querySelectorAll('[data-equipment-key]').forEach((input) => {
            const key = input.dataset.equipmentKey
            const quantity = Number(input.value)
            if (key && Number.isInteger(quantity) && quantity > 0) details[key] = quantity
          })
          payload.equipment_details = details
          requestInit = { ...requestInit, body: JSON.stringify(payload) }
        }
      } catch (error) {
        console.error('Could not add selected equipment to the booking request.', error)
      }
    }

    let response = await nativeFetch(input, requestInit)
    const requestHeaders = new Headers(requestInit?.headers || (input instanceof Request ? input.headers : undefined))
    const authorization = requestHeaders.get('Authorization') || requestHeaders.get('authorization')
    if (response.status === 401 && authorization?.startsWith('Bearer ') && !/\/auth\/token\/refresh\/?$/.test(requestPath)) {
      const accessToken = await refreshAccessToken()
      if (accessToken) {
        requestHeaders.set('Authorization', 'Bearer'.concat(' ', accessToken))
        response = await nativeFetch(input, { ...requestInit, headers: requestHeaders })
      }
    }

    if (!response.ok) {
      try {
        const body = await response.clone().json()
        if (body.error && typeof body.error === 'object') {
          const wrapped = body.error
          const message = formatApiError(wrapped.details) || formatApiError(wrapped.message)
          if (message) {
            return new Response(JSON.stringify({ ...body, error: message }), {
              status: response.status,
              statusText: response.statusText,
              headers: response.headers,
            })
          }
        }
      } catch (error) {
        console.error('Could not parse the API error response.', error)
      }
    }
    return response
  }

  const equipmentUi = {
    ru: { quantity: 'Количество', none: 'Для этой категории экипировка не указана.', loadError: 'Не удалось загрузить экипировку площадки.', required: 'Укажите количество экипировки для аренды.' },
    en: { quantity: 'Quantity', none: 'No equipment is configured for this sport category.', loadError: 'Could not load equipment for this court.', required: 'Enter the equipment quantities you want to rent.' },
    tk: { quantity: 'Mukdary', none: 'Bu sport kategoriýasy üçin enjamlar görkezilmedi.', loadError: 'Meýdançanyň enjamlaryny ýükläp bolmady.', required: 'Kärendesine almak üçin enjamlaryň sanyny görkeziň.' },
  }

  function localizedEquipmentName(name, fallback) {
    if (typeof name === 'string') return name || fallback
    if (!name || typeof name !== 'object') return fallback
    return name[lang()] || name.ru || name.en || name.tk || fallback
  }

  async function loadBookingEquipment(form) {
    const courtId = activeBookingCourtId
    if (!courtId || equipmentLoadId === courtId) return
    equipmentLoadId = courtId

    const checkbox = form.querySelector('[name="equipment_needed"]')
    const fields = form.querySelector('[data-preview-equipment-fields]')
    if (!checkbox || !fields) return
    checkbox.disabled = true
    fields.innerHTML = ''
    fields.hidden = true

    try {
      const response = await nativeFetch(`/api/v1/courts/${encodeURIComponent(courtId)}/`, {
        headers: { Accept: 'application/json' },
      })
      if (!response.ok) throw new Error(`Court details request failed with HTTP ${response.status}`)
      const court = await response.json()
      if (activeBookingCourtId !== courtId || !form.isConnected) return

      const equipment = court.category_info?.available_equipment
      const labels = equipmentUi[lang()] || equipmentUi.ru
      if (!Array.isArray(equipment) || equipment.length === 0) {
        checkbox.checked = false
        checkbox.disabled = true
        fields.innerHTML = `<p class="preview-equipment-none">${labels.none}</p>`
        fields.hidden = false
        return
      }

      checkbox.disabled = false
      fields.innerHTML = `
        ${equipment.map((item) => {
          const key = String(item?.key || '')
          if (!key) return ''
          const name = localizedEquipmentName(item.name_i18n, key)
          return `<label>${escapeHtml(name)} — ${escapeHtml(labels.quantity)}
            <input name="equipment_quantity_${escapeHtml(key)}" data-equipment-key="${escapeHtml(key)}" type="number" min="0" step="1" value="0">
          </label>`
        }).join('')}
        <p class="preview-equipment-error" data-preview-equipment-error hidden>${labels.required}</p>
      `
      if (!fields.querySelector('[data-equipment-key]')) {
        checkbox.disabled = true
        fields.innerHTML = `<p class="preview-equipment-none">${labels.none}</p>`
        fields.hidden = false
        return
      }
      fields.hidden = !checkbox.checked
    } catch (error) {
      if (activeBookingCourtId === courtId && form.isConnected) {
        checkbox.checked = false
        checkbox.disabled = true
        const labels = equipmentUi[lang()] || equipmentUi.ru
        fields.innerHTML = `<p class="preview-equipment-none">${labels.loadError}</p>`
        fields.hidden = false
      }
      console.error('Failed to load equipment for the selected court.', error)
    }
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    })[character])
  }

  function enhanceBookingForm() {
    const form = document.querySelector('[data-form="booking"]')
    const checkbox = form?.querySelector('[name="equipment_needed"]')
    if (!form || !checkbox || form.querySelector('[data-preview-equipment-fields]')) return

    checkbox.disabled = true
    const fields = document.createElement('div')
    fields.className = 'preview-equipment-quantities'
    fields.dataset.previewEquipmentFields = 'true'
    fields.hidden = true
    checkbox.closest('label, .option-row')?.after(fields)
    loadBookingEquipment(form)
  }

  document.addEventListener('change', (event) => {
    if (event.target.matches('[name="equipment_needed"]')) {
      const fields = document.querySelector('[data-preview-equipment-fields]')
      const error = document.querySelector('[data-preview-equipment-error]')
      if (fields) fields.hidden = !event.target.checked
      if (error) error.hidden = true
    }
  }, true)

  document.addEventListener('submit', (event) => {
    const form = event.target
    if (!form.matches('[data-form="booking"]')) return
    const checkbox = form.querySelector('[name="equipment_needed"]')
    if (!checkbox?.checked) return
    const hasQuantity = [...form.querySelectorAll('[data-equipment-key]')].some((input) => {
      const quantity = Number(input.value)
      return Number.isInteger(quantity) && quantity > 0
    })
    if (hasQuantity) return

    event.preventDefault()
    event.stopImmediatePropagation()
    const error = form.querySelector('[data-preview-equipment-error]')
    if (error) error.hidden = false
  }, true)

  document.addEventListener('click', (event) => {
    const bookButton = event.target.closest('[data-book]')
    if (bookButton) {
      activeBookingCourtId = bookButton.dataset.book
      equipmentLoadId = null
      return
    }
    if (event.target.closest('[data-action="close-drawer"]')) {
      activeBookingCourtId = null
      equipmentLoadId = null
    }
  }, true)

  function closeTournamentDialog() {
    document.querySelector('.preview-tournament-backdrop')?.remove()
    updateScrollLock()
  }

  function updateScrollLock() {
    document.body.classList.toggle(
      'preview-scroll-locked',
      Boolean(document.querySelector('.side-drawer, .preview-tournament-backdrop')),
    )
  }

  function openTournamentDialog(button) {
    closeTournamentDialog()
    const card = button.closest('.tournament-card, .card')
    if (!card) return

    const langCode = lang()
    const status = card.querySelector('.status-pill')?.textContent?.trim().toLowerCase() || ''
    const openStatuses = {
      ru: ['регистрация открыта', 'open'],
      en: ['registration open', 'open'],
      tk: ['hasaba alyş açyk', 'open'],
    }[langCode] || ['registration open', 'open']
    const participantText = card.querySelectorAll('.meta-list li')[2]?.textContent || ''
    const capacity = participantText.match(/(\d+)\s*\/\s*(\d+)/)
    const hasSpots = !capacity || Number(capacity[2]) === 0 || Number(capacity[1]) < Number(capacity[2])
    const canRegister = openStatuses.includes(status) && hasSpots
    const registrationButton = card.querySelector('[data-register-tournament]')
    const content = card.cloneNode(true)
    content.querySelector('[data-register-tournament], [data-tournament-details]')?.remove()

    const dialog = document.createElement('section')
    dialog.className = 'preview-tournament-dialog'
    dialog.setAttribute('role', 'dialog')
    dialog.setAttribute('aria-modal', 'true')
    dialog.setAttribute('aria-label', card.querySelector('h3')?.textContent?.trim() || 'Tournament details')
    dialog.innerHTML = '<button class="preview-tournament-close" type="button" aria-label="Close">×</button>'
    dialog.append(content)

    if (canRegister && registrationButton) {
      const register = document.createElement('button')
      register.className = 'orange-btn full'
      register.type = 'button'
      register.dataset.previewRegister = registrationButton.dataset.registerTournament || ''
      register.textContent = ({ ru: 'Зарегистрироваться', en: 'Register', tk: 'Hasaba ýazylmak' })[langCode] || 'Register'
      dialog.append(register)
    }

    const backdrop = document.createElement('div')
    backdrop.className = 'preview-tournament-backdrop'
    backdrop.append(dialog)
    document.body.append(backdrop)
    updateScrollLock()
  }

  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-preview-register], .preview-tournament-close, .preview-tournament-backdrop, [data-tournament-details], [data-register-tournament]')
    if (!target) return

    if (event.target.matches('.preview-tournament-backdrop') || target.matches('.preview-tournament-close')) {
      event.preventDefault()
      event.stopImmediatePropagation()
      closeTournamentDialog()
      return
    }

    if (target.matches('[data-preview-register]')) {
      event.preventDefault()
      event.stopImmediatePropagation()
      const tournamentId = target.dataset.previewRegister
      const sourceButton = [...document.querySelectorAll('[data-register-tournament]')]
        .find((button) => button.dataset.registerTournament === tournamentId)
      if (sourceButton) {
        sourceButton.dataset.previewRegistrationConfirmed = 'true'
        closeTournamentDialog()
        sourceButton.click()
      }
      return
    }

    if (target.matches('[data-register-tournament]') && target.dataset.previewRegistrationConfirmed === 'true') {
      delete target.dataset.previewRegistrationConfirmed
      return
    }

    event.preventDefault()
    event.stopImmediatePropagation()
    openTournamentDialog(target)
  }, true)

  const appRoot = document.querySelector('#app')
  if (appRoot) {
    new MutationObserver(updateScrollLock).observe(appRoot, { childList: true, subtree: true })
  }

  function lang() {
    return document.querySelector('[data-field="language"]')?.value || 'ru'
  }

  function buttons() {
    const copy = translations[lang()] || translations.ru
    const actions = document.createElement('div')
    actions.className = 'download-actions'
    actions.innerHTML = `
      <a class="download-button download-android" href="/downloads/sportlink.apk" download>${copy.android}</a>
      <button class="download-button download-iphone" type="button" data-preview-ios>${copy.iphone}</button>
    `
    return actions
  }

  function renderHome() {
    iosPage = false
    const phone = document.querySelector('.phone-mock, .hero-phone')
    if (phone && (
      !phone.classList.contains('hero-phone')
      || phone.querySelector('img')?.getAttribute('src') !== mockupSrc
    )) {
      phone.className = 'hero-phone'
      phone.innerHTML = `<img src="${mockupSrc}" alt="Sportlink app screenshot">`
    }

    document.querySelectorAll('.store-row').forEach((row) => {
      row.replaceWith(buttons())
    })
  }

  function renderIosPage() {
    iosPage = true
    const copy = translations[lang()] || translations.ru
    const app = document.querySelector('#app')
    const header = app?.querySelector('.topbar')?.outerHTML || ''
    const footer = app?.querySelector('.footer')
    if (!app) return

    if (footer) {
      footer.querySelectorAll('.store-row').forEach((row) => row.replaceWith(buttons()))
    }

    app.innerHTML = `
      ${header}
      <main class="ios-install-page shell">
        <article class="ios-install-card">
          <h1>${copy.title}</h1>
          <p>${copy.intro}</p>
          <ol class="ios-install-steps">${copy.steps.map((step) => `<li>${step}</li>`).join('')}</ol>
          <p class="ios-install-note">${copy.note}</p>
          <button class="orange-btn" type="button" data-preview-home>${copy.back}</button>
        </article>
      </main>
      ${footer?.outerHTML || ''}
    `
  }

  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-preview-ios], [data-preview-home]')
    if (!target) return

    event.preventDefault()
    event.stopImmediatePropagation()

    if (target.hasAttribute('data-preview-ios')) {
      history.pushState({}, '', '/ios-installation')
      renderIosPage()
    } else {
      history.pushState({}, '', '/')
      iosPage = false
      window.dispatchEvent(new PopStateEvent('popstate'))
    }
  }, true)

  window.addEventListener('popstate', () => {
    if (location.pathname === '/ios-installation') renderIosPage()
    else iosPage = false
  })

  document.addEventListener('input', (event) => {
    if (event.target.matches('[data-field="language"]') && iosPage) {
      queueMicrotask(renderIosPage)
    }
  }, true)

  const observer = new MutationObserver(() => {
    enhanceBookingForm()
    if (location.pathname === '/ios-installation') {
      if (!iosPage) renderIosPage()
      return
    }
    renderHome()
  })

  observer.observe(document.querySelector('#app'), { childList: true, subtree: true })
  enhanceBookingForm()
  renderHome()

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js').catch((error) => {
      console.error('Failed to register the Sportlink service worker.', error)
    })
  }
})()
