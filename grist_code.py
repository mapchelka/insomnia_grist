import grist
from functions import *       # global uppercase functions
import datetime, math, re     # modules commonly needed in formulas


@grist.UserTable
class Access_rules:

  def _default_username(rec, table, value, user):
    return rec.person.name
  username = grist.Text()
  Email = grist.Text()
  Organizer = grist.Bool()
  HR = grist.Bool()
  Table_Creator = grist.Bool()
  Food_court = grist.Bool()
  headquarters = grist.Bool()
  IT = grist.Bool()
  Branch = grist.Bool()

  def _default_is_people(rec, table, value, user):
    return People.lookupOne(emailList=CONTAINS(rec.Email.strip().lower())) == rec.person if rec.person else None
  is_people = grist.Bool()
  BL_admin = grist.Bool()
  Specialist = grist.Bool()
  Bus = grist.Bool()
  speciality = grist.ChoiceList()

  @grist.formulaType(grist.Reference('People'))
  def person(rec, table):
    return People.lookupOne(emailList=CONTAINS(rec.Email.strip().lower()))

  def person_telegram_norm_TF(rec, table):
    return rec.person.telegram_norm_TF

  @grist.formulaType(grist.Reference('People'))
  def possible_person(rec, table):
    if rec.person:
      return None

    person_by_email = People.lookupOne(emailList=CONTAINS(rec.Email.strip().lower()))
    if person_by_email:
      return person_by_email

    username = rec.username.strip().split()

    if len(username) == 1:
    	person_by_nickname = People.lookupOne(nickname=rec.username, order_by='id')
    	if person_by_nickname:
    	  return person_by_nickname

    	person_by_name = People.lookupOne(name=rec.username, order_by='id')
    	if person_by_name:
    	  return person_by_name

    if len(username) == 2:
    	person_by_first_last_name = People.lookupOne(first_name=username[0].capitalize(), last_name=username[1].capitalize(), order_by='id')
    	if person_by_first_last_name:
    	  return person_by_first_last_name

    	person_by_last_first_name = People.lookupOne(last_name=username[0].capitalize(), first_name=username[1].capitalize(), order_by='id')
    	if person_by_last_first_name:
    	  return person_by_last_first_name

  @grist.formulaType(grist.Text())
  def view_as(rec, table):
    return f"[см]({SELF_HYPERLINK(page=101)}?aclAsUser_={rec.Email})"

  @grist.formulaType(grist.Bool())
  def isHRLead(rec, table):
    if rec.person and rec.HR:
      for role in ('ORGANIZER', 'VICE'):
        if Participation.lookupOne(person=rec.person, role_code=role, is_current_year=True):
          return True

    return False

  @grist.formulaType(grist.ReferenceList('Teams'))
  def thisYearOrgViceTeams(rec, table):
    if not rec.person:
        return None

    records = Participation.lookupRecords(person=rec.person, is_current_year=True)
    return list(set(r.team for r in records if r.role_code in ('ORGANIZER', 'VICE', 'TEAM_LEAD')))

  @grist.formulaType(grist.ReferenceList('Teams'))
  def thisYearOrgTeams(rec, table):
    if rec.Organizer and rec.person:
      return Participation.lookupRecords(person=rec.person, role_code='ORGANIZER', is_current_year=True).team


@grist.UserTable
class Application_form:
  name = grist.Text()

  def _default_birth_year(rec, table, value, user):
    return YEAR(rec.birth_date)
  birth_year = grist.Numeric()
  city = grist.Text()
  telegram = grist.Text()
  phone = grist.Text()
  email = grist.Text()
  social_networks = grist.Text()
  about = grist.Text()
  preferred_activity = grist.Text()
  experience = grist.ChoiceList()
  acquaintances = grist.Text()
  stages = grist.ChoiceList()
  time_on_the_field = grist.Choice()
  first_check_in = grist.Choice()
  time_to_stay_after = grist.Choice()
  getting_to_the_field_by = grist.Choice()
  comments = grist.Text()
  personal_data_agreement = grist.Bool()
  answer_urgency = grist.Choice()
  tags = grist.ReferenceList('Application_states')

  def _default_created(rec, table, value, user):
    return NOW(tz="Europe/Moscow")
  created = grist.DateTime('Europe/Moscow')
  coordinator = grist.Reference('People')

  def _default_telegram_link(rec, table, value, user):
    return ('https://t.me/'+rec.telegram_norm_TF) if rec.telegram_norm_TF else ''
  telegram_link = grist.Text()
  src = grist.Text()
  call_me = grist.Choice()
  notes = grist.Text()
  user = grist.Text()
  birth_date = grist.Date()
  status = grist.Reference('Application_states')

  def _default_phone_norm_TF(rec, table, value, user):
    s=''.join(filter(str.isnumeric,rec.phone))
    if len(s)==10:
      return s
    elif len(s)==11 and s[0] in '78':
      return s[1:]
    return None
  phone_norm_TF = grist.Text()

  def _default_email_norm_TF(rec, table, value, user):
    return IFERROR(lambda: (re.search(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", rec.email.lower()).group()),"")
  email_norm_TF = grist.Text()

  def _default_telegram_norm_TF(rec, table, value, user):
    return IFERROR(lambda: (re.search(r"(?:(?<!\S)@|(?:(?:https?://)?(?:t\.me|telegram\.(?:me|dog))/|tg://resolve\?domain=)|(?=\b(?!\w*__)(?!\w*_{2,})(?:[a-z][a-z0-9_]{3,31})(?<!_)\.t\.me$))(?P<username>(?!\w*_{2,})(?!\w*[^0-9a-z_.,\s])(?:[a-z][a-z0-9_]{3,31})(?<!_)\b)(?:\.t\.me)?", rec.telegram.lower(), re.MULTILINE | re.VERBOSE).group(1)),"")
  telegram_norm_TF = grist.Text()

  def _default_row_id(rec, table, value, user):
    return rec.id
  row_id = grist.Int()

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()

  def _default_last_updated_at(rec, table, value, user):
    return NOW()
  last_updated_at = grist.DateTime('Europe/Moscow')
  have_ticket = grist.Bool()

  def _default_created_thisyear(rec, table, value, user):
    return rec.created.date() > Calendar.lookupOne(is_current_year=True).year_start_dt
  created_thisyear = grist.Bool()
  gender = grist.Choice()
  accepted_team = grist.Reference('Teams')
  recommended_direction = grist.ReferenceList('Teams')

  @grist.formulaType(grist.Bool())
  def isInBL(rec, table):
    for p in rec.people_dup:
      if p.isInBL != "Нет":
        return True
    return False

  @grist.formulaType(grist.ReferenceList('Application_form'))
  def Application_dup(rec, table):
    ts, es, ps = set(), set(), set()
    if rec.telegram_norm_TF:
      ts = {t for t in Application_form.lookupRecords(telegram_norm_TF=rec.telegram_norm_TF, created_thisyear=True ) if t.id!=rec.id}
    if rec.phone_norm_TF:
      ps = {p for p in Application_form.lookupRecords(phone_norm_TF=rec.phone_norm_TF, created_thisyear=True ) if p.id!=rec.id}
    if rec.email_norm_TF:
      es = {e for e in Application_form.lookupRecords(email_norm_TF=rec.email_norm_TF, created_thisyear=True ) if e.id!=rec.id}  
    return set().union(ts,es,ps)

  @grist.formulaType(grist.ReferenceList('People'))
  def people_dup(rec, table):
    ts, es, ps = set(), set(), set()
    if rec.telegram_norm_TF:
      ts = {t for t in People.lookupRecords(telegram_norm_TF=rec.telegram_norm_TF )}
    if rec.phone_norm_TF:
      ps = {p for p in People.lookupRecords(phone_norm_TF=CONTAINS(rec.phone_norm_TF) ) }
    if rec.email_norm_TF:
      es = {e for e in People.lookupRecords(email_norm_TF=rec.email_norm_TF ) }  
    return set().union(ts,es,ps)

  @grist.formulaType(grist.Int())
  def coordinator_filter(rec, table):
    return 0

  @grist.formulaType(grist.ReferenceList('Application_form'))
  def Application_old_dup(rec, table):
    ts, es, ps = set(), set(), set()
    if rec.telegram_norm_TF:
      ts = {t for t in Application_form.lookupRecords(telegram_norm_TF=rec.telegram_norm_TF, created_thisyear=False ) if t.id!=rec.id}
    if rec.phone_norm_TF:
      ps = {p for p in Application_form.lookupRecords(phone_norm_TF=rec.phone_norm_TF, created_thisyear=False ) if p.id!=rec.id}
    if rec.email_norm_TF:
      es = {e for e in Application_form.lookupRecords(email_norm_TF=rec.email_norm_TF, created_thisyear=False ) if e.id!=rec.id}  
    return set().union(ts,es,ps)

  def curator_mails(rec, table):
    return rec.coordinator.emailList

  @grist.formulaType(grist.Reference('People'))
  def last_updated_by_nik(rec, table):
    return Access_rules.lookupOne(Email=rec.last_updated_by).person

  @grist.formulaType(grist.Text())
  def form_card(rec, table):
    return f"[{rec.row_id}]({SELF_HYPERLINK(page=11)}#a1.s84.r{rec.id})"
    #(https://grist.insomniafest.ru/mhwDM83vLmT3/Insomnia/p/11#a1.s173.r{$id})"
    #

  @grist.formulaType(grist.Int())
  def age(rec, table):
    if not rec.birth_date:
        return None

    # Дата первого заезда волонтеров на поле
    first_arrival = Calendar.lookupOne(is_current_year=True).arrival_dt

    # Считаем разницу: текущий год минус год рождения
    age = first_arrival.year - rec.birth_date.year

    # Корректируем возраст, если день рождения в этом году еще не наступил
    if (first_arrival.month, first_arrival.day) < (rec.birth_date.month, rec.birth_date.day):
        age -= 1

    return age


@grist.UserTable
class Application_states:
  title = grist.Text()
  description = grist.Text()
  use_for = grist.Choice()
  color = grist.Text()


@grist.UserTable
class Applications_for_design_and_printing_2025:
  A = grist.Text()

  def _default_B(rec, table, value, user):
    return ["Не в работе"]
  B = grist.ChoiceList()
  E = grist.Text()
  F = grist.Bool()
  G = grist.Text()
  H = grist.Text()
  I = grist.Bool()
  J = grist.Text()
  K = grist.Text()
  L = grist.Attachments()
  M = grist.Text()
  C = grist.ReferenceList('People')
  N = grist.Text()
  O = grist.ChoiceList()
  P = grist.Attachments()

  def _default_Last_updated_by(rec, table, value, user):
    return user.Email
  Last_updated_by = grist.Text()

  def _default_Last_updated_at(rec, table, value, user):
    return NOW()
  Last_updated_at = grist.DateTime('Europe/Moscow')
  D = grist.Reference('Direction_2025')


@grist.UserTable
class Applications_for_design_and_printing_2026:
  A = grist.Text()
  C = grist.Text()
  D = grist.Text()
  E = grist.Text()
  G = grist.Text()
  H = grist.Text()
  I = grist.ChoiceList()

  def _default_J(rec, table, value, user):
    return user.Name
  J = grist.Text()

  def _default_F(rec, table, value, user):
    return NOW()
  F = grist.Text()

  def _default_K(rec, table, value, user):
    return NOW()
  K = grist.DateTime('Europe/Moscow')
  L = grist.ChoiceList()
  B = grist.ReferenceList('Direction')


@grist.UserTable
class Arrival_type:
  title = grist.Text()
  code = grist.Text()
  icon = grist.Text()


@grist.UserTable
class Arrival_yearly:
  engagement_participation_page_link = grist.Text()
  arrival_date = grist.Date()

  def _default_arrival_transport(rec, table, value, user):
    return value if value else Arrival_type.lookupOne(code='UNDEFINED')
  arrival_transport = grist.Reference('Arrival_type')
  arrival_registered = grist.DateTime('Europe/Moscow')
  departure_date = grist.Date()

  def _default_departure_transport(rec, table, value, user):
    return value if value else Arrival_type.lookupOne(code='UNDEFINED')
  departure_transport = grist.Reference('Arrival_type')
  departure_registered = grist.DateTime('Europe/Moscow')
  extra_data = grist.Text()
  comment = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_UUID(rec, table, value, user):
    if value:
      return value
    else:
      return SUBSTITUTE(UUID(),"-","")
  UUID = grist.Text()
  to_delete = grist.DateTime('Europe/Moscow')
  delete_reason = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()

  def _default_updated_by(rec, table, value, user):
    return user.Email
  updated_by = grist.Text()

  def _default_badge(rec, table, value, user):
    # при любом изменении заезда без бейджа пытаемся найти бейдж по персоне в связанном участии
    return Badge_yearly.lookupOne(person=rec.engagement.person) if rec.engagement and not value else value
  badge = grist.Reference('Badge_yearly')
  bus_promo = grist.Reference('Bus_promo_yearly', reverse_of='arrivals')

  def _default_status(rec, table, value, user):
    return value if (rec.badge and value) else Participation_status.lookupOne(code=IF(rec.badge,lambda: ("PLANNED"),lambda: ("UNDEFINED")))
  status = grist.Reference('Participation_status')
  engagement = grist.Reference('Participation', reverse_of='arrivals_ref')

  @grist.formulaType(grist.Int())
  def infant_age(rec, table):
    from datetime import date

    adult = 18
    age = adult
    if rec.engagement and rec.engagement.person and rec.engagement.person.birth_date and rec.arrival_date:
        birth_date = rec.engagement.person.birth_date
        target_date = rec.arrival_date
        age = target_date.year - birth_date.year - ((target_date.month, target_date.day) < (birth_date.month, birth_date.day))
    
    return age if age < adult else None

  def person_id(rec, table):
    return rec.badge.person.id if rec.badge else rec.engagement.person.id

  def title(rec, table):
    if not rec.arrival_date: return "⭕️ нет даты заезда ⭕️"
    if not rec.departure_date: return "⭕️ нет даты выезда ⭕️"
    return f"{rec.arrival_transport.icon}{rec.arrival_date.strftime('%d.%-m')} – {rec.departure_date.strftime('%d.%-m')}{rec.departure_transport.icon} {rec.status.icon}"

  def status_color(rec, table):
    return rec.status.color

  @grist.formulaType(grist.Bool())
  def is_bus(rec, table):
    return not rec.to_delete \
    and ((rec.arrival_transport.title=="На автобусе") \
      or (rec.departure_transport.title=="На автобусе"))

  @grist.formulaType(grist.Reference('Parking_yearly'))
  def parking(rec, table):
    return Parking_yearly.lookupOne(person=rec.engagement.person)

  @grist.formulaType(grist.Bool())
  def is_transport_arranged(rec, table):
    return True if rec.parking or rec.bus_promo else False

  def arrival_day_list(rec, table):
    from datetime import timedelta

    # Если участие отменено или даты не заполнены, возвращаем пустой список
    if rec.to_delete or rec.status.color == 'red' or not rec.arrival_date or not rec.departure_date:
      return []

    # Вычисляем количество дней между заездом и выездом
    days_count = (rec.departure_date - rec.arrival_date).days

    # Генерируем список дат от заезда до выезда включительно
    return [rec.arrival_date + timedelta(days=i) for i in range(days_count + 1)]

  @grist.formulaType(grist.Reference('People'))
  def person(rec, table):
    return rec.engagement.person

  def person_telegram(rec, table):
    return rec.engagement.person.telegram

  def row_id(rec, table):
    return rec.id

  def person_mix(rec, table):
    if rec.engagement and rec.badge:
      return rec.engagement.person == rec.badge.person
    else:
      return None

  @grist.formulaType(grist.DateTime('Europe/Moscow'))
  def feeder_update_at(rec, table):
    return None

  @grist.formulaType(grist.ReferenceList('Problems'))
  def problem_list(rec, table):
    # Если запись помечена на удаление, выходим сразу
    if rec.to_delete:
      return None

    # Загружаем ошибки Заездов
    prob_map = {p.code: p for p in Problems.lookupRecords(entity='Заезд') if p.code}

    error_list = []

    # Кэшируем поля текущей строки для ускорения работы Python
    arr_date = rec.arrival_date
    dep_date = rec.departure_date
    status_code = rec.status.code if rec.status else None
    status_color = rec.status.color if rec.status else None

    # --- Блок проверок ---

    # Нет даты заезда
    if not arr_date:
      error_list.append(prob_map.get('A.NoArrivalDate'))

    # Неполное заполнение
    if not (arr_date and dep_date and rec.status and rec.arrival_transport and rec.departure_transport):
      error_list.append(prob_map.get('A.NotAllFields'))

    # Пора подтверждать (прямое вычитание дат без тяжелой функции DATEDIF)
    if arr_date and status_code in ['PLANNED', 'PENDING', 'UNDEFINED']:
      if (arr_date - TODAY()).days < 5:
        error_list.append(prob_map.get('A.TimeToConfirm'))

    # Заезд позже отъезда
    if arr_date and dep_date and arr_date > dep_date:
      error_list.append(prob_map.get('A.ArrivalAfterDeparture'))

    # Пересечение заездов (один запрос к базе вместо циклов)
    if arr_date and dep_date and rec.badge:
      same_badge_arrivals = Arrival_yearly.lookupRecords(badge=rec.badge, to_delete=None)
      for a in same_badge_arrivals:
        if a.id != rec.id and a.arrival_date and a.departure_date:
          if a.arrival_date <= dep_date and arr_date <= a.departure_date:
            error_list.append(prob_map.get('A.ArrivalsCrossing'))
            break

    # Ранний заезд
    if arr_date and status_code in ['PLANNED', 'PENDING', 'UNDEFINED'] and arr_date < DATE(2026, 6, 5):
      error_list.append(prob_map.get('A.EarlyArrivalDate'))

    # Нужен промокод
    if rec.is_bus and not rec.bus_promo:
      error_list.append(prob_map.get('A.NoBusPromo'))

    # Не по расписанию (чистый поиск без IFERROR)
    if status_color == 'green':
      if rec.arrival_transport.code == 'BUS' and arr_date:
        if not Bus_Days_2026.lookupRecords(date=arr_date):
          error_list.append(prob_map.get('A.NotOnSchedule'))
      
      if rec.departure_transport.code == 'BUS' and dep_date:
        if not Bus_Days_2026.lookupRecords(date=dep_date):
          error_list.append(prob_map.get('A.NotOnSchedule'))

    # Не записана машина на парковку
    if 'CAR' in (rec.arrival_transport.code, rec.departure_transport.code) and not rec.parking:
      error_list.append(prob_map.get('A.NoParking'))

    # Возвращаем список, защищенный от None
    return [e for e in error_list if e]

  @grist.formulaType(grist.Reference('Badge_yearly'))
  def A(rec, table):
    return rec.engagement.badge[0]

  @grist.formulaType(grist.Reference('Badge_yearly'))
  def feeder_update_by(rec, table):
    return 0

  @grist.formulaType(grist.Reference('Teams'))
  def team_ref(rec, table):
    return rec.engagement.team

  class _Summary:

    @grist.formulaType(grist.Int())
    def arrival_cnt(rec, table):
      return len([gr for gr in rec.group if not gr.to_delete and gr.status.color != 'red'])

    def gristHelper_Display(rec, table):
      return rec.person.name

    @grist.formulaType(grist.ReferenceList('Arrival_yearly'))
    def group(rec, table):
      return table.getSummarySourceGroup(rec)

    def gristHelper_Display2(rec, table):
      return rec.team_list.team_name

    @grist.formulaType(grist.Text())
    def june_01_10(rec, table):
      return Lib.lookupOne().get_arrival_bar(rec.group.arrival_day_list, 1, 10, 6)

    @grist.formulaType(grist.Text())
    def june_11_20(rec, table):
      return Lib.lookupOne().get_arrival_bar(rec.group.arrival_day_list, 11, 20, 6)

    @grist.formulaType(grist.Text())
    def june_21_30(rec, table):
      return Lib.lookupOne().get_arrival_bar(rec.group.arrival_day_list, 21, 30, 6)

    @grist.formulaType(grist.Text())
    def july_01_10(rec, table):
      return Lib.lookupOne().get_arrival_bar(rec.group.arrival_day_list, 1, 10, 7)

    @grist.formulaType(grist.Text())
    def july_11_20(rec, table):
      return Lib.lookupOne().get_arrival_bar(rec.group.arrival_day_list, 11, 20, 7)

    @grist.formulaType(grist.Text())
    def july_21_31(rec, table):
      return Lib.lookupOne().get_arrival_bar(rec.group.arrival_day_list, 21, 31, 7)

    @grist.formulaType(grist.ReferenceList('Teams'))
    def team_list(rec, table):
      return list(set([gr.team_ref for gr in rec.group if not gr.to_delete and gr.status.color != 'red']))


@grist.UserTable
class Arrivals_20240904:
  arrival_date = grist.Date()
  arrival_transport_id = grist.Text()
  departure_date = grist.Date()
  departure_transport_id = grist.Text()
  status = grist.Text()
  badge_id = grist.Text()
  id2 = grist.Text()
  created_at = grist.DateTime('Europe/Moscow')
  updated_at = grist.DateTime('Europe/Moscow')
  status_link = grist.Reference('Participation_status')
  status_name = grist.Reference('Participation_status')

  @grist.formulaType(grist.Reference('Badges_2024'))
  def badge(rec, table):
    return Badges_2024.lookupOne(uuid=rec.badge_id)


@grist.UserTable
class Arrivals_2025:

  def _default_badge(rec, table, value, user):
    return Badges_2025.lookupOne(person=rec.engagement.person) if rec.engagement else value
  badge = grist.Reference('Badges_2025')
  arrival_date = grist.Date()

  def _default_arrival_transport(rec, table, value, user):
    return value if value else Arrival_type.lookupOne(code='UNDEFINED')
  arrival_transport = grist.Reference('Arrival_type')
  arrival_registered = grist.DateTime('Europe/Moscow')
  departure_date = grist.Date()

  def _default_departure_transport(rec, table, value, user):
    return value if value else Arrival_type.lookupOne(code='UNDEFINED')
  departure_transport = grist.Reference('Arrival_type')
  departure_registered = grist.DateTime('Europe/Moscow')
  extra_data = grist.Text()
  comment = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_UUID(rec, table, value, user):
    if value:
      return value
    else:
      return SUBSTITUTE(UUID(),"-","")
  UUID = grist.Text()
  to_delete = grist.DateTime('Europe/Moscow')
  delete_reason = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_status(rec, table, value, user):
    return value if (rec.badge and value) else Participation_status.lookupOne(code=IF(rec.badge,lambda: ("PLANNED"),lambda: ("UNDEFINED")))
  status = grist.Reference('Participation_status')
  engagement = grist.Reference('Participation')

  def person_id(rec, table):
    return rec.badge.person.id if rec.badge else rec.engagement.person.id

  def title(rec, table):
    if not rec.arrival_date: return "⭕️ нет даты заезда ⭕️"
    if not rec.departure_date: return "⭕️ нет даты выезда ⭕️"
    return f"{rec.arrival_transport.icon}{rec.arrival_date.strftime('%d.%-m')} – {rec.departure_date.strftime('%d.%-m')}{rec.departure_transport.icon} {rec.status.icon}"

  @grist.formulaType(grist.Text())
  def engagement_participation_2025_link(rec, table):
    return rec.engagement.participation_page_link

  def status_color(rec, table):
    return rec.status.color

  @grist.formulaType(grist.ReferenceList('Problems'))
  def problem_list(rec, table):
    error_list = []
    if not(rec.arrival_date):
      error_list.append( Problems.lookupOne(code='A.NoArrivalDate'))
    if not( rec.arrival_date and rec.departure_date and rec.status and rec.arrival_transport and rec.departure_transport) :
      error_list.append( Problems.lookupOne(code='A.NotAllFields'))
    if rec.arrival_date and rec.status.code in  ['PLANNED','PENDING','UNDEFINED'] and DATEDIF(TODAY(), rec.arrival_date, "D") < 5:
      error_list.append( Problems.lookupOne(code='A.TimeToConfirm'))
    if rec.arrival_date and rec.departure_date and rec.arrival_date > rec.departure_date:
      error_list.append( Problems.lookupOne(code='A.ArrivalAfterDeparture'))
    if not(rec.to_delete) and rec.arrival_date and rec.departure_date and rec.badge:
      for a in Arrivals_2025.lookupRecords(badge=rec.badge, to_delete=None):
        if  a.id != rec.id and a.arrival_date and a.departure_date and a.arrival_date <= rec.departure_date and rec.arrival_date <= a.departure_date:
          error_list.append( Problems.lookupOne(code='A.ArrivalsCrossing'))
          break
    if (rec.arrival_date) and rec.status.code in  ['PLANNED','PENDING','UNDEFINED'] and rec.arrival_date < DATE(2025,6,17):
      error_list.append( Problems.lookupOne(code='A.EarlyArrivalDate'))

    if rec.arrival_transport.code == 'BUS' and rec.status.color == 'green':
       dtf_list = IFERROR(lambda: (Bus_passenger_yearly.lookupRecords(badge=rec.badge, approve = True).day_to_fest.date), None)
       if dtf_list and not(rec.arrival_date in dtf_list):
         error_list.append( Problems.lookupOne(code='A.NoBus'))
    if rec.departure_transport.code == 'BUS' and rec.status.color == 'green':
       dff_list = IFERROR(lambda: (Bus_passenger_yearly.lookupRecords(badge=rec.badge, approve = True).day_from_fest.date), None)
       if dff_list and not(rec.departure_date in dff_list):
         error_list.append( Problems.lookupOne(code='A.NoBus'))

    return error_list


@grist.UserTable
class Badge_yearly:

  def _default_gender(rec, table, value, user):
    return rec.person.gender if rec.person else value
  gender = grist.Choice()
  person = grist.Reference('People')

  def _default_phone(rec, table, value, user):
    return rec.person.phone if rec.person else value
  phone = grist.Text()

  def _default_infant(rec, table, value, user):
    return IFERROR(lambda: (rec.person_is_infant), False)
  infant = grist.Bool()

  def _default_name(rec, table, value, user):
    if rec.batch>1: return rec.str_source
    return rec.str1 + ' ' + rec.str2 if rec.str2 else rec.str1
  name = grist.Text()

  def _default_diet(rec, table, value, user):
    return 'Веган' if rec.vegan else 'Без особенностей'
  diet = grist.Choice()

  def _default_feed_type(rec, table, value, user):
    return 'Бесплатно' if rec.role.isFeed else 'Без питания'
  feed_type = grist.Choice()

  def _default_number(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      return ( str(rec.role.id) if rec.role else 'X' ) + '-' + (str(rec.directions_ref[0].id).rjust(3,'0') if rec.directions_ref else 'xxx') + '-' + str(rec.number_in_role).rjust(3,'0')
  number = grist.Text()
  batch = grist.Int()

  def _default_status(rec, table, value, user):
    return IF(rec.person, lambda: ('Автоподстановка'), lambda: ('Новый'))
  status = grist.Choice()

  def _default_role(rec, table, value, user):
    return IFERROR(lambda: (rec.sorted_engagement[0].role if rec.person else value),None)
  role = grist.Reference('Roles')

  def _default_position(rec, table, value, user):
    if rec.batch > 0: return rec.position_source
    return rec.position1 + ' ' + rec.position2 if rec.position2 else rec.position1
  position = grist.Text()

  def _default_photo(rec, table, value, user):
    #подставляет фото для привязанного человека только если не указано имя файла явно
    return Photo.lookupOne(person=rec.person,isForBage=True) if (rec.person and not rec.filename.strip()) else None
  photo = grist.Reference('Photo')
  comment = grist.Text()

  def _default_ticket(rec, table, value, user):
    return True if rec.tickets_ref else False
  ticket = grist.Bool()

  def _default_str1(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 15
      s = rec.str_source
      if len(s) <= MAX_LEN:
        return s
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return s
      else:
        return s[:pos]
  str1 = grist.Text()

  def _default_str2(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 15
      s = rec.str_source
      if len(s) <= MAX_LEN:
        return ''
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return ''
      else:
        return s[pos+1:]
  str2 = grist.Text()

  def _default_last_name(rec, table, value, user):
    return rec.person.last_name.strip() if rec.person else value.strip()
  last_name = grist.Text()

  def _default_first_name(rec, table, value, user):
    return rec.person.first_name.strip() if rec.person else value.strip()
  first_name = grist.Text()

  def _default_direction1(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >0:
        return rec.directions_ref[0].name_for_badge if rec.directions_ref[0].name_for_badge else rec.directions_ref[0].team_name
      else:
        return None
  direction1 = grist.Text()

  def _default_direction2(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >1:
        return rec.directions_ref[1].name_for_badge if rec.directions_ref[1].name_for_badge else rec.directions_ref[1].team_name
      else:
        return None
  direction2 = grist.Text()

  def _default_direction3(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >2:
        return rec.directions_ref[2].name_for_badge if rec.directions_ref[2].name_for_badge else rec.directions_ref[2].team_name
      else:
        return None
  direction3 = grist.Text()

  def _default_direction4(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >3:
        return rec.directions_ref[3].name_for_badge if rec.directions_ref[3].name_for_badge else rec.directions_ref[3].team_name
      else:
        return None
  direction4 = grist.Text()

  def _default_direction5(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >4:
        tms = [ (d.name_for_badge if d.name_for_badge else d.team_name) for d in rec.directions_ref]
        s = ','.join( tms[4:])
        return s[:20]
      else:
        return None
  direction5 = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_UUID(rec, table, value, user):
    return value if value else SUBSTITUTE(UUID(),"-","")
  UUID = grist.Text()

  def _default_position1(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 22
      s = rec.position_source
      if len(s) <= MAX_LEN:
        return s
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return s
      else:
        return s[:pos]
  position1 = grist.Text()

  def _default_position2(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 22
      s = rec.position_source
      if len(s) <= MAX_LEN:
        return ''
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return ''
      else:
        return s[pos+1:]
  position2 = grist.Text()
  trigger = grist.Bool()

  def _default_position_source(rec, table, value, user):
    ret = ''
    if not (rec.person): return value
    if rec.person.id == 0: return rec.role.Name
    for p in rec.sorted_engagement:
        if p.position:
            ret += ' ' + p.position
        else:
            if p.role.Color in ['Зеленый','Синий']:
                ret += ' ' + p.team.name_for_badge if p.team.name_for_badge else p.team.team_name
            elif p.role.Color.startswith('Красно-'):
                ret += ' ' + p.role.Name + ' ' + \
                  p.team.name_for_badge if p.team.name_for_badge else p.team.team_name
            else:
                ret += ' ' + p.role.Name
    return ret.strip()
  position_source = grist.Text()

  def _default_str_source(rec, table, value, user):
    return rec.person.name if rec.person else value
  str_source = grist.Text()
  to_delete = grist.DateTime('Europe/Moscow')
  photo_upload = grist.Attachments()

  def _default_Last_updated_by(rec, table, value, user):
    return user.Email
  Last_updated_by = grist.Text()
  filename = grist.Text()

  def _default_vegan(rec, table, value, user):
    return rec.person.vegan if rec.person else value
  vegan = grist.Bool()
  delete_reason = grist.Text()
  no_ticket = grist.Bool()
  feeder_update = grist.DateTime('Europe/Moscow')
  tickets_ref = grist.ReferenceList('Tickets', reverse_of='badges_2025_ref')
  parent = grist.Reference('Badge_yearly')

  def _default_number_in_role(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if rec.no_directions:
        ref = Badge_yearly.lookupRecords(no_directions=True)
        return PEEK(lambda: (MAX(ref.number_in_role))) +1
      vals = [0]
      for d in rec.directions_ref:
        refs = Badge_yearly.lookupRecords(directions_ref=CONTAINS(d))
        for b in refs:
          if not(ISERROR(lambda: (PEEK(lambda: (b.number_in_role))))):
            vals.append(PEEK(lambda: (b.number_in_role)))
      return max(vals) +1
  number_in_role = grist.Int()
  import_batch = grist.Reference('Import_series_yearly')

  def _default_directions_ref(rec, table, value, user):
    if rec.sorted_engagement:
      return [e.team for e in rec.sorted_engagement if e.team ]
    elif rec.parent and ISREF(rec.parent):
      return [rec.parent.directions_ref]
    else:
      return value
  directions_ref = grist.ReferenceList('Teams')

  @grist.formulaType(grist.Attachments())
  def photo_photo(rec, table):
    return rec.photo.photo if rec.person else rec.photo_upload

  @grist.formulaType(grist.Bool())
  def no_directions(rec, table):
    return not (rec.directions_ref and ISREFLIST(rec.directions_ref))

  @grist.formulaType(grist.Text())
  def photo_file(rec, table):
    if rec.photo_attach_id:
      return str(rec.photo_attach_id)+'.jpg'
    fn = rec.filename.strip()
    if fn and rec.import_batch:
      ext=fn.split(".")[-1].lower()
      res = rec.import_batch.folder_name + '/' + fn
      if not ext in ("jpg","jpeg","png","webp"):
        res += '.jpg'
      return res
    return "заглушка.jpg"

  @grist.formulaType(grist.Int())
  def photo_attach_id(rec, table):
    try: 
      return rec.photo_photo[0].id if rec.photo_photo else None
    except: 
      return None

  @grist.formulaType(grist.Text())
  def maket(rec, table):
    return rec.role.Color + IF(rec.infant,lambda: ('_ребенок'),lambda: (''))

  def phone_norm_TF(rec, table):
    norm_tels = []
    tlist = rec.phone.split(',')
    for tel in tlist:
      s=''.join(filter(str.isnumeric,tel))
      if len(s)<10:
        pass
      if len(s)==10:
        norm_tels.append(s)
      elif len(s)==11 and s[0] in '78':
        norm_tels.append(s[1:])
    return norm_tels

  @grist.formulaType(grist.Text())
  def page_link(rec, table):
    return f"[бейдж]({SELF_HYPERLINK(page=90)}#a1.s305.r{rec.id})"

  @grist.formulaType(grist.Reference('Arrivals_2025'))
  def arrival4ticket(rec, table):
    for a in Arrivals_2025.lookupRecords(badge=rec.id, to_delete=None):
        if (a.arrival_date) and a.arrival_date >= DATE(2025,7,16) and a.arrival_date <= DATE(2025,7,20) and a.status.code in ("PLANNED", "CONFIRMED", "UNDEFINED"):
          return a

  @grist.formulaType(grist.Bool())
  def person_is_infant(rec, table):
    if not rec.person.birth_date:
        return None

    # Дата первого заезда волонтеров на поле 
    first_arrival = Calendar.lookupOne(is_current_year=True).arrival_dt

    # Считаем разницу: текущий год минус год рождения
    age = first_arrival.year - rec.person.birth_date.year

    # Корректируем возраст, если день рождения в этом году еще не наступил
    if (first_arrival.month, first_arrival.day) < (rec.person.birth_date.month, rec.person.birth_date.day):
        age -= 1

    return age < 18 if age else None

  def row_id(rec, table):
    return rec.id

  @grist.formulaType(grist.DateTime('Europe/Moscow'))
  def feeder_update_at(rec, table):
    return None

  @grist.formulaType(grist.ReferenceList('Badge_yearly'))
  def doubles_by_name(rec, table):
    return [b for b in Badge_yearly.lookupRecords(last_name=rec.last_name, first_name=rec.first_name, to_delete=None) if b.id != rec.id] if len(rec.first_name) >0 and len(rec.last_name) > 0 else None

  @grist.formulaType(grist.ReferenceList('Badge_yearly'))
  def doubles_by_person(rec, table):
    return [b for b in Badge_yearly.lookupRecords(person=rec.person, to_delete = None) if b.id != rec.id] if (rec.person)  else None

  @grist.formulaType(grist.Reference('Badge_yearly'))
  def feeder_update_by(rec, table):
    return 0

  @grist.formulaType(grist.ReferenceList('Participation'))
  def sorted_engagement(rec, table):
    # если есть связанный человек, выводятся все его участия в текущем году, 
    # отсортированные по роли. Нужно для определения значений по умолчанию
    if rec.person:
      return sorted(filter(lambda r: r.status.color!='red',
      Participation.lookupRecords(person=rec.person, year=2026))
      ,key=lambda r: r.role.priority)

  @grist.formulaType(grist.ReferenceList('Problems'))
  def problem_list(rec, table):
    # Загружаем ошибки Бейджей
    prob_map = {p.code: p for p in Problems.lookupRecords(entity='Бейдж')}

    # Получаем Заезды
    arrivals = Arrival_yearly.lookupRecords(badge=rec.id, to_delete=None)

    # --- Блок проверок ---
    error_list = []

    if not rec.role: 
      error_list.append(prob_map.get('B.NoRole'))

    if not rec.first_name or not rec.last_name: 
      error_list.append(prob_map.get('B.NoName'))

    if rec.role and rec.role.need_person and not rec.person: 
      error_list.append(prob_map.get('B.NoPerson'))

    if rec.person and (rec.first_name != rec.person.first_name or rec.last_name != rec.person.last_name or rec.gender != rec.person.gender):
      error_list.append(prob_map.get('B.PersonNameDiffer'))

    if not arrivals: 
      error_list.append(prob_map.get('B.NoArrivals'))

    if rec.doubles_by_person or (rec.doubles_by_name and not rec.person) : 
      error_list.append(prob_map.get('B.Doubles'))

    # Проверка на НСЛ
    if rec.person_is_infant and not rec.infant:
      error_list.append(prob_map.get('B.NoInfantFlag'))

    # Проверка наличия С кем для НСЛ
    if (rec.role.Code == 'FELLOW' or rec.infant) and not (rec.parent and ISREF(rec.parent)): 
      error_list.append(prob_map.get('B.NoParent'))

    # Проверка длины строк
    def is_long(val, max_len=20):
      return bool(val) and len(val) > max_len

    if (is_long(rec.str1, 15) or is_long(rec.str2, 15) or 
        is_long(rec.position1) or is_long(rec.position2) or 
        is_long(rec.direction1) or is_long(rec.direction2) or 
        is_long(rec.direction3) or is_long(rec.direction4) or 
        is_long(rec.direction5)):
      error_list.append(prob_map.get('B.LongStrings'))

    # Проверки по уже загруженному списку arrivals
    if any(len(a.problem_list) > 0 for a in arrivals):
      error_list.append(prob_map.get('B.ArrivalsProblems'))

    if (rec.role.Code != "FELLOW") and (not (rec.ticket or rec.no_ticket)):
      for a in arrivals:
        if a.arrival_date and DATE(2026,7,8) <= a.arrival_date <= DATE(2026,7,12) and a.status.code in ("PLANNED", "CONFIRMED", "UNDEFINED") and a.arrival_transport.code != "MOVE":
          error_list.append(prob_map.get('B.NoTicket'))
          break

    # Проверки участий (Participations)
    if rec.person:
      # Кэшируем участия в рамках строки
      parts_2026 = Participation.lookupRecords(person=rec.person, year=2026, status_color='green')
  
      if not parts_2026 and any(a.status_color == 'green' for a in arrivals):
        error_list.append(prob_map.get('B.NoParticipation'))
    
      if set(rec.directions_ref) != set(p.team for p in parts_2026):
        error_list.append(prob_map.get('B.TeamsNotEqual'))

      # Проверка отсутствия С кем (нужно только детям и плюсодинам) 
      if rec.parent and parts_2026 and rec.role.Code!='FELLOW' and not rec.person_is_infant:
        error_list.append(prob_map.get('B.ParentUnnecessary'))    

    # Возвращаем список, отфильтровав пустые значения (None) на случай опечаток в кодах
    return [e for e in error_list if e]

  @grist.formulaType(grist.ReferenceList('Teams'))
  def A(rec, table):
    return rec.parent.directions_ref

  @grist.formulaType(grist.ReferenceList('Teams'))
  def sorted_engagement____(rec, table):
    return rec.sorted_engagement.team

  @grist.formulaType(grist.Reference('Teams'))
  def import_batch__(rec, table):
    return rec.import_batch.team


@grist.UserTable
class Badges_2024:
  uuid = grist.Text()
  notion_id = grist.Text()
  person_id = grist.Text()
  name = grist.Text()
  last_name = grist.Text()
  first_name = grist.Text()
  gender_id = grist.Text()
  team_name = grist.Text()
  team_id = grist.Text()
  main_role_id = grist.Text()
  position = grist.Text()
  is_vegan = grist.Numeric()
  feed_type = grist.Text()
  is_blocked = grist.Numeric()
  phone = grist.Text()
  comment = grist.Text()
  printing_batch = grist.Numeric()
  created_at = grist.Text()
  updated_at = grist.Text()
  deleted_at = grist.Text()
  arrival_status = grist.Text()

  def _default_person(rec, table, value, user):
    return IF(rec.person_id.isalnum(), lambda: (People.lookupOne(ntn_id=rec.person_id)),lambda: (''))
  person = grist.Reference('People')
  role = grist.Reference('Roles')

  @grist.formulaType(grist.Text())
  def HR(rec, table):
    return ''

  @grist.formulaType(grist.ReferenceList('Teams'))
  def teams(rec, table):
    from uuid import UUID
    res = set()
    for i in rec.team_id.split():
      res.add(Teams.lookupOne(UUID=str(UUID(i))))
    return list(res)


@grist.UserTable
class Badges_2025:

  def _default_gender(rec, table, value, user):
    return rec.person.gender if rec.person else value
  gender = grist.Choice()
  person = grist.Reference('People')

  def _default_phone(rec, table, value, user):
    return rec.person.phone if rec.person else value
  phone = grist.Text()

  def _default_infant(rec, table, value, user):
    return IFERROR( lambda: (False if rec.person.birth_date  < DATE(2007,7,1) else True), False)
  infant = grist.Bool()

  def _default_diet(rec, table, value, user):
    return 'Веган' if rec.vegan else 'Без особенностей'
  diet = grist.Choice()

  def _default_feed_type(rec, table, value, user):
    return 'Бесплатно' if rec.role.isFeed else 'Без питания'
  feed_type = grist.Choice()

  def _default_number(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      return ( str(rec.role.id) if rec.role else 'X' ) + '-' + (str(rec.directions_ref[0].id).rjust(3,'0') if rec.directions_ref else 'xxx') + '-' + str(rec.number_in_role).rjust(3,'0')
  number = grist.Text()
  batch = grist.Int()

  def _default_role(rec, table, value, user):
    return IFERROR(lambda: (rec.sorted_engagement[0].role if rec.person else value),None)
  role = grist.Reference('Roles')

  def _default_position(rec, table, value, user):
    if rec.batch > 0: return rec.position_source
    return rec.position1 + ' ' + rec.position2 if rec.position2 else rec.position1
  position = grist.Text()

  def _default_photo(rec, table, value, user):
    return Photo.lookupOne(person=rec.person,isForBage=True) if rec.person else None
  photo = grist.Reference('Photo')
  comment = grist.Text()
  parent = grist.Reference('Badges_2025')

  def _default_ticket(rec, table, value, user):
    return True if rec.tickets_ref else False
  ticket = grist.Bool()

  def _default_name(rec, table, value, user):
    if rec.batch>1: return rec.str_source
    return rec.str1 + ' ' + rec.str2 if rec.str2 else rec.str1
  name = grist.Text()

  def _default_last_name(rec, table, value, user):
    return rec.person.last_name.strip() if rec.person else value.strip()
  last_name = grist.Text()

  def _default_first_name(rec, table, value, user):
    return rec.person.first_name.strip() if rec.person else value.strip()
  first_name = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_UUID(rec, table, value, user):
    return value if value else SUBSTITUTE(UUID(),"-","")
  UUID = grist.Text()

  def _default_number_in_role(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if rec.no_directions:
        ref = Badges_2025.lookupRecords(no_directions=True)
        return PEEK(lambda: (MAX(ref.number_in_role))) +1
      vals = [0]
      for d in rec.directions_ref:
        refs = Badges_2025.lookupRecords(directions_ref=CONTAINS(d))
        for b in refs:
          if not(ISERROR(lambda: (PEEK(lambda: (b.number_in_role))))):
            vals.append(PEEK(lambda: (b.number_in_role)))
      return max(vals) +1
  number_in_role = grist.Int()

  def _default_str1(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 15
      s = rec.str_source
      if len(s) <= MAX_LEN:
        return s
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return s
      else:
        return s[:pos]
  str1 = grist.Text()

  def _default_str2(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 15
      s = rec.str_source
      if len(s) <= MAX_LEN:
        return ''
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return ''
      else:
        return s[pos+1:]
  str2 = grist.Text()

  def _default_position1(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 22
      s = rec.position_source
      if len(s) <= MAX_LEN:
        return s
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return s
      else:
        return s[:pos]
  position1 = grist.Text()

  def _default_position2(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      MAX_LEN = 22
      s = rec.position_source
      if len(s) <= MAX_LEN:
        return ''
      pos = s.find(' ',min(len(s) // 2, MAX_LEN), MAX_LEN+1)
      if pos == -1: pos = s.rfind(' ',0,min(len(s) // 2, MAX_LEN))
      if pos == -1: 
        return ''
      else:
        return s[pos+1:]
  position2 = grist.Text()

  def _default_status(rec, table, value, user):
    return IF(rec.person, lambda: ('Автоподстановка'), lambda: ('Новый'))
  status = grist.Choice()

  def _default_position_source(rec, table, value, user):
    ret = ''
    if not (rec.person): return value
    if rec.person.id == 0: return rec.role.Name
    for p in rec.sorted_engagement:
        if p.position:
            ret += ' ' + p.position
        else:
            if p.role.Color in ['Зеленый','Синий']:
                ret += ' ' + p.team.name_for_badge if p.team.name_for_badge else p.team.team_name
            elif p.role.Color.startswith('Красно-'):
                ret += ' ' + p.role.Name + ' ' + \
                  p.team.name_for_badge if p.team.name_for_badge else p.team.team_name
            else:
                ret += ' ' + p.role.Name
    return ret.strip()
  position_source = grist.Text()
  to_delete = grist.DateTime('Europe/Moscow')

  def _default_Last_updated_by(rec, table, value, user):
    return user.Email
  Last_updated_by = grist.Text()
  filename = grist.Text()
  photo_upload = grist.Attachments()

  def _default_vegan(rec, table, value, user):
    return rec.person.vegan if rec.person else value
  vegan = grist.Bool()

  def _default_str_source(rec, table, value, user):
    return rec.person.name if rec.person else value
  str_source = grist.Text()
  trigger = grist.Bool()

  def _default_direction1(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >0:
        return rec.directions_ref[0].name_for_badge if rec.directions_ref[0].name_for_badge else rec.directions_ref[0].team_name
      else:
        return None
  direction1 = grist.Text()

  def _default_direction2(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >1:
        return rec.directions_ref[1].name_for_badge if rec.directions_ref[1].name_for_badge else rec.directions_ref[1].team_name
      else:
        return None
  direction2 = grist.Text()

  def _default_direction3(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >2:
        return rec.directions_ref[2].name_for_badge if rec.directions_ref[2].name_for_badge else rec.directions_ref[2].team_name
      else:
        return None
  direction3 = grist.Text()

  def _default_direction4(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >3:
        return rec.directions_ref[3].name_for_badge if rec.directions_ref[3].name_for_badge else rec.directions_ref[3].team_name
      else:
        return None
  direction4 = grist.Text()

  def _default_direction5(rec, table, value, user):
    if rec.batch >0:
      return value
    else:
      if len(rec.directions_ref) >4:
        tms = [ (d.name_for_badge if d.name_for_badge else d.team_name) for d in rec.directions_ref]
        s = ','.join( tms[4:])
        return s[:20]
      else:
        return None
  direction5 = grist.Text()
  delete_reason = grist.Text()
  tickets_ref = grist.Reference('Tickets')
  no_ticket = grist.Bool()
  import_batch = grist.Reference('Import_series_yearly')

  def _default_directions_ref(rec, table, value, user):
    if rec.sorted_engagement:
      return [e.team for e in rec.sorted_engagement if e.team ]
    elif rec.parent and ISREF(rec.parent):
      return [rec.parent.directions_ref]
    else:
      return value
  directions_ref = grist.ReferenceList('Teams')

  @grist.formulaType(grist.Attachments())
  def photo_photo(rec, table):
    return rec.photo.photo if rec.person else rec.photo_upload

  @grist.formulaType(grist.Int())
  def photo_attach_id(rec, table):
    try: 
      return rec.photo_photo[0].id if rec.photo_photo else None
    except: 
      return None

  @grist.formulaType(grist.Text())
  def maket(rec, table):
    return rec.role.Color + IF(rec.infant,lambda: ('_ребенок'),lambda: (''))

  @grist.formulaType(grist.Text())
  def photo_file(rec, table):
    if rec.photo_attach_id:
      return str(rec.photo_attach_id)+'.jpg'
    fn = rec.filename.strip()
    if fn and rec.import_batch:
      res = rec.import_batch.folder_name + '/' + fn
      if not (res.endswith('.jpg') or res.endswith('.jpeg')):
        res += '.jpg'
      return res
    return "заглушка.jpg"

  def phone_norm_TF(rec, table):
    norm_tels = []
    tlist = rec.phone.split(',')
    for tel in tlist:
      s=''.join(filter(str.isnumeric,tel))
      if len(s)<10:
        pass
      if len(s)==10:
        norm_tels.append(s)
      elif len(s)==11 and s[0] in '78':
        norm_tels.append(s[1:])
    return norm_tels

  @grist.formulaType(grist.Bool())
  def no_directions(rec, table):
    return not (rec.directions_ref and ISREFLIST(rec.directions_ref))

  @grist.formulaType(grist.ReferenceList('Badges_2025'))
  def doubles_by_name(rec, table):
    return [b for b in Badges_2025.lookupRecords(last_name=rec.last_name, first_name=rec.first_name, to_delete=None) if b.id != rec.id] if len(rec.first_name) >0 and len(rec.last_name) > 0 else None

  @grist.formulaType(grist.ReferenceList('Badges_2025'))
  def doubles_by_person(rec, table):
    return [b for b in Badges_2025.lookupRecords(person=rec.person, to_delete = None) if b.id != rec.id] if (rec.person)  else None

  @grist.formulaType(grist.Text())
  def page_link(rec, table):
    return f"[бейдж]({SELF_HYPERLINK(page=38)}#a1.s103.r{rec.id})"

  @grist.formulaType(grist.Reference('Arrivals_2025'))
  def arrival4ticket(rec, table):
    for a in Arrivals_2025.lookupRecords(badge=rec.id, to_delete=None):
        if (a.arrival_date) and a.arrival_date >= DATE(2025,7,16) and a.arrival_date <= DATE(2025,7,20) and a.status.code in ("PLANNED", "CONFIRMED", "UNDEFINED"):
          return a

  @grist.formulaType(grist.ReferenceList('Participation'))
  def sorted_engagement(rec, table):
    return sorted(filter(lambda r: r.status.color!='red',
      Participation.lookupRecords(person=rec.person,year=2025))
      ,key=lambda r: r.role.priority)

  @grist.formulaType(grist.ReferenceList('Problems'))
  def problem_list(rec, table):
    error_list = []
    if not(rec.role): 
      error_list.append( Problems.lookupOne(code='B.NoRole'))
    if len(rec.first_name) == 0 or len(rec.last_name) == 0: 
      error_list.append( Problems.lookupOne(code='B.NoName'))
    if rec.role and rec.role.need_person and not(rec.person): 
      error_list.append( Problems.lookupOne(code='B.NoPerson'))
    if rec.person and (rec.first_name != rec.person.first_name or rec.last_name != rec.person.last_name or rec.gender != rec.person.gender):
      error_list.append( Problems.lookupOne(code='B.PersonNameDiffer'))
    if not(Arrivals_2025.lookupOne(badge=rec.id, to_delete=None)): 
      error_list.append( Problems.lookupOne(code='B.NoArrivals'))
    if (rec.role.Code == 'FELLOW' or rec.infant) and not(rec.parent and ISREF(rec.parent)): 
      error_list.append( Problems.lookupOne(code='B.NoParent'))
    if len(rec.doubles_by_name) > 0 or len(rec.doubles_by_person) >0: 
      error_list.append(Problems.lookupOne(code='B.Doubles'))

    def check_len(value, max_len=20):
      return bool(value) and len(value) > max_len

    if check_len(rec.str1, 15) or check_len(rec.str2, 15) or \
        check_len(rec.position1) or check_len(rec.position2) or \
        any(map(check_len,(rec.direction1,rec.direction2,rec.direction3,rec.direction4,rec.direction5))):
      error_list.append(Problems.lookupOne(code='B.LongStrings'))
    for a in Arrivals_2025.lookupRecords(badge=rec.id,to_delete=None):
      if len(a.problem_list) > 0:
        error_list.append(Problems.lookupOne(code='B.ArrivalsProblems'))
        break
    if not(rec.ticket or rec.no_ticket):
      for a in Arrivals_2025.lookupRecords(badge=rec.id, to_delete=None):
        if (a.arrival_date) and a.arrival_date >= DATE(2025,7,16) and a.arrival_date <= DATE(2025,7,20) and a.status.code in ("PLANNED", "CONFIRMED", "UNDEFINED"):
          error_list.append(Problems.lookupOne(code='B.NoTicket'))
          break

    if (rec.person) and not(Participation.lookupOne(person=rec.person,year=2025,status_color='green'))  and \
       (Arrivals_2025.lookupOne(badge=rec.id,status_color='green', to_delete=None)):
      error_list.append(Problems.lookupOne(code='B.NoParticipation'))
    if (rec.person) and not(set(rec.directions_ref) == set(Participation.lookupRecords(person=rec.person,year=2025,status_color='green').team) ):
      error_list.append(Problems.lookupOne(code='B.TeamsNotEqual'))

    return error_list


@grist.UserTable
class Black_list_comment:

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()
  type = grist.Choice()
  comment = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_author(rec, table, value, user):
    return Access_rules.lookupOne(Email=rec.created_by).username
  author = grist.Text()
  inBlackList = grist.Bool()
  whats_wrong = grist.ChoiceList()
  about_who = grist.Reference('People')


@grist.UserTable
class Bus_Cars_2026:
  title = grist.Text()
  bus_day = grist.Reference('Bus_Days_2026')
  capasity = grist.Int()

  def _default_datetime(rec, table, value, user):
    return rec.bus_day.date
  datetime = grist.DateTime('Europe/Moscow')

  @grist.formulaType(grist.ReferenceList('Bus_Passengers_2026'))
  def passengers(rec, table):
    return Bus_Passengers_2026.lookupRecords(bus_to_fest=rec.id) if rec.bus_day.to_fest  else Bus_Passengers_2026.lookupRecords(bus_from_fest=rec.id) 

  @grist.formulaType(grist.Int())
  def count(rec, table):
    return len(rec.passengers)


@grist.UserTable
class Bus_Days_2026:
  date = grist.Date()
  time = grist.Text()
  route = grist.Choice()
  comment = grist.Text()
  limit = grist.Int()
  deadline = grist.DateTime('Europe/Moscow')

  def _default_status(rec, table, value, user):
    return 'Запись'
  status = grist.Choice()

  def _default_to_fest(rec, table, value, user):
    return rec.route[-1] == 'Б'
  to_fest = grist.Bool()

  @grist.formulaType(grist.Text())
  def title(rec, table):
    res = [rec.date.strftime("%d.%m"), rec.route]
    if rec.time: res.append(rec.time)

    if rec.status in ('Ушёл','Закрыто'):
      res.append(f"({rec.status})")
    elif rec.status == 'До лимита':
      free = rec.limit - rec.count
      if free <= 0:
        res.append('(Нет мест)')
      elif free < 10:
        res.append(f'({free} мест)')

    return ' '.join(res)

  @grist.formulaType(grist.Bool())
  def closed(rec, table):
    return rec.status in ('Закрыто', 'Ушёл') or (rec.status == 'До лимита' and rec.count >= rec.limit)

  def undistributed(rec, table):
    return len(Bus_Passengers_2026.lookupRecords(day_to_fest=rec.id,status='Всё верно',bus_to_fest=None)
    ) + \
    len(Bus_Passengers_2026.lookupRecords(day_from_fest=rec.id,status='Всё верно',bus_from_fest=None)) 

  def count(rec, table):
    return len(rec.passengers) + \
    len(Bus_Passengers_2026.lookupRecords(day_to_fest=rec.id,status='Ждём данных')
    ) + \
    len(Bus_Passengers_2026.lookupRecords(day_from_fest=rec.id,status='Ждём данных')) 

  @grist.formulaType(grist.ReferenceList('Bus_passenger_yearly'))
  def passengers(rec, table):
    return list(Bus_Passengers_2026.lookupRecords(day_to_fest=rec.id,status='Всё верно')) + list(Bus_Passengers_2026.lookupRecords(day_from_fest=rec.id,status='Всё верно')) 


@grist.UserTable
class Bus_Passengers_2026:

  def _default_status(rec, table, value, user):
    return "Всё верно" if rec.approve else "Черновик"
  status = grist.Choice()

  def _default_role(rec, table, value, user):
    return rec.badge.role
  role = grist.Reference('Roles')

  def _default_ln(rec, table, value, user):
    return value if rec.approve else rec.badge.last_name
  ln = grist.Text()

  def _default_fn(rec, table, value, user):
    return value if rec.approve else rec.badge.first_name
  fn = grist.Text()
  sn = grist.Text()

  def _default_bd(rec, table, value, user):
    return value if rec.approve else rec.badge.person.birth_date
  bd = grist.Date()
  document = grist.Text()

  def _default_day_to_fest(rec, table, value, user):
    return rec.bus_to_fest.day if rec.bus_to_fest else value
  day_to_fest = grist.Reference('Bus_Days_2026')

  def _default_phone(rec, table, value, user):
    return value if rec.approve else rec.badge.phone
  phone = grist.Text()
  approve = grist.Bool()
  comment = grist.Text()

  def _default_Last_updated_by(rec, table, value, user):
    return user.Email if value else Access_rules.lookupOne(username=rec.added_by).Email
  Last_updated_by = grist.Text()

  def _default_Last_updated_at(rec, table, value, user):
    return NOW()
  Last_updated_at = grist.DateTime('Europe/Moscow')
  status_to_fest = grist.Choice()
  status_from_fest = grist.Choice()

  def _default_gender(rec, table, value, user):
    return value if rec.approve else rec.badge.gender
  gender = grist.Choice()

  def _default_added_by(rec, table, value, user):
    return Access_rules.lookupOne(Email=user.Email).username
  added_by = grist.Text()
  badge = grist.Reference('Badge_yearly')
  day_from_fest = grist.Reference('Bus_route_yearly')
  bus_to_fest = grist.Reference('Bus_car_yearly')
  bus_from_fest = grist.Reference('Bus_car_yearly')

  def _default_team(rec, table, value, user):
    return rec.badge.directions_ref[0] if rec.badge.directions_ref else None
  team = grist.Reference('Teams')

  @grist.formulaType(grist.Bool())
  def closed(rec, table):
    return (rec.day_to_fest.closed and rec.bus_to_fest.day != rec.day_to_fest) \
    or (rec.day_from_fest.closed and rec.bus_from_fest.day != rec.day_from_fest)

  @grist.formulaType(grist.Text())
  def tel(rec, table):
    s=''.join(filter(str.isnumeric,rec.phone))
    if len(s)<10:
      return '_¿'+rec.phone.strip() + '?_'
    if len(s)==10:
      pass
    elif len(s)==11 and s[0] in '78':
      s=s[1:]
    return f"[({s[0:3]}){s[3:]}](tel:+7{s})"

  @grist.formulaType(grist.Bool())
  def Duplicates(rec, table):
    return (bool(rec.badge) and len(Bus_Passengers_2026.lookupRecords(badge=rec.badge)) > 1) or len(Bus_Passengers_2026.lookupRecords(ln=rec.ln,fn=rec.fn,sn=rec.sn))>1


@grist.UserTable
class Bus_car_yearly:
  title = grist.Text()
  capasity = grist.Int()

  def _default_datetime(rec, table, value, user):
    return rec.day.date
  datetime = grist.DateTime('Europe/Moscow')
  day = grist.Reference('Bus_route_yearly')

  @grist.formulaType(grist.Int())
  def count(rec, table):
    return len(rec.passengers)

  @grist.formulaType(grist.ReferenceList('Bus_passenger_yearly'))
  def passengers(rec, table):
    return Bus_passenger_yearly.lookupRecords(bus_to_fest=rec.id) or Bus_passenger_yearly.lookupRecords(bus_from_fest=rec.id) 


@grist.UserTable
class Bus_passenger_yearly:
  badge = grist.Reference('Badges_2025')

  def _default_role(rec, table, value, user):
    return rec.badge.role
  role = grist.Reference('Roles')

  def _default_ln(rec, table, value, user):
    return value if rec.approve else rec.badge.last_name
  ln = grist.Text()

  def _default_fn(rec, table, value, user):
    return value if rec.approve else rec.badge.first_name
  fn = grist.Text()
  sn = grist.Text()

  def _default_bd(rec, table, value, user):
    return value if rec.approve else rec.badge.person.birth_date
  bd = grist.Date()
  document = grist.Text()
  approve = grist.Bool()
  comment = grist.Text()

  def _default_phone(rec, table, value, user):
    return value if rec.approve else rec.badge.phone
  phone = grist.Text()

  def _default_Last_updated_by(rec, table, value, user):
    return user.Email if value else Access_rules.lookupOne(username=rec.added_by).Email
  Last_updated_by = grist.Text()

  def _default_Last_updated_at(rec, table, value, user):
    return NOW()
  Last_updated_at = grist.DateTime('Europe/Moscow')

  def _default_added_by(rec, table, value, user):
    return Access_rules.lookupOne(Email=user.Email).username
  added_by = grist.Text()

  def _default_gender(rec, table, value, user):
    return value if rec.approve else rec.badge.gender
  gender = grist.Choice()
  status_to_fest = grist.Choice()
  status_from_fest = grist.Choice()

  def _default_status(rec, table, value, user):
    return "Всё верно" if rec.approve else "Черновик"
  status = grist.Choice()

  def _default_day_to_fest(rec, table, value, user):
    return rec.bus_to_fest.day if rec.bus_to_fest else value
  day_to_fest = grist.Reference('Bus_route_yearly')
  day_from_fest = grist.Reference('Bus_route_yearly')
  bus_to_fest = grist.Reference('Bus_car_yearly')
  bus_from_fest = grist.Reference('Bus_car_yearly')

  def _default_team(rec, table, value, user):
    return rec.badge.directions_ref[0] if rec.badge.directions_ref else None
  team = grist.Reference('Teams')

  @grist.formulaType(grist.Text())
  def tel(rec, table):
    s=''.join(filter(str.isnumeric,rec.phone))
    if len(s)<10:
      return '_¿'+rec.phone.strip() + '?_'
    if len(s)==10:
      pass
    elif len(s)==11 and s[0] in '78':
      s=s[1:]
    return f"[({s[0:3]}){s[3:]}](tel:+7{s})"

  @grist.formulaType(grist.Bool())
  def closed(rec, table):
    return (rec.day_to_fest.closed and rec.bus_to_fest.day != rec.day_to_fest) \
    or (rec.day_from_fest.closed and rec.bus_from_fest.day != rec.day_from_fest)

  @grist.formulaType(grist.Bool())
  def Duplicates(rec, table):
    return (bool(rec.badge) and len(Bus_passenger_yearly.lookupRecords(badge=rec.badge)) > 1) or len(Bus_passenger_yearly.lookupRecords(ln=rec.ln,fn=rec.fn,sn=rec.sn))>1


@grist.UserTable
class Bus_promo_yearly:
  promocode = grist.Text()

  def _default_issued_at(rec, table, value, user):
    if rec.arrivals:
      return NOW()
    else:
      return value
  issued_at = grist.DateTime('Europe/Moscow')

  def _default_issued_by(rec, table, value, user):
    if rec.arrivals:
      return user.Email
    else:
      return value
  issued_by = grist.Text()
  to_delete = grist.Bool()
  comment = grist.Text()

  def _default_promo_year(rec, table, value, user):
    return YEAR(NOW())
  promo_year = grist.Text()

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_updated_by(rec, table, value, user):
    return user.Email
  updated_by = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')
  arrivals = grist.Reference('Arrival_yearly', reverse_of='bus_promo')

  @grist.formulaType(grist.Int())
  def discount(rec, table):
    return 0

  def arrivals_person_name(rec, table):
    return rec.arrivals.engagement.person.name

  def A(rec, table):
    return None

  @grist.formulaType(grist.Bool())
  def is_double(rec, table):
    return rec.id != Bus_promo_yearly.lookupOne(promocode=rec.promocode, sort_by="created_at").id

  @grist.formulaType(grist.Bool())
  def is_top(rec, table):
    import itertools

    # Ограничиваем кол-во в выпадающем списке в Заездах
    top = 5

    # Создаем легковесный генератор, который лениво перебирает свободные билеты
    available_gen = (
        b.id for b in Bus_promo_yearly.all 
        if not b.arrivals 
           and not b.is_double 
           and not b.to_delete
    )

    # Вытаскиваем из генератора ровно первые 5 ID и сразу прекращаем перебор
    top_5_available = list(itertools.islice(available_gen, top))

    # Проверяем, входит ли текущий билет в эту пятерку
    return rec.id in top_5_available


@grist.UserTable
class Bus_route_yearly:
  date = grist.Date()
  route = grist.Choice()
  comment = grist.Text()
  limit = grist.Int()

  def _default_to_fest(rec, table, value, user):
    return rec.route[-1] == 'Б'
  to_fest = grist.Bool()
  deadline = grist.DateTime('Europe/Moscow')

  def _default_status(rec, table, value, user):
    return 'Запись'
  status = grist.Choice()

  @grist.formulaType(grist.Text())
  def time(rec, table):
    return ''

  @grist.formulaType(grist.Text())
  def title(rec, table):
    res = [rec.date.strftime("%d.%m"), rec.route]
    if rec.time: res.append(rec.time)

    if rec.status in ('Ушёл','Закрыто'):
      res.append(f"({rec.status})")
    elif rec.status == 'До лимита':
      free = rec.limit - rec.count
      if free <= 0:
        res.append('(Нет мест)')
      elif free < 10:
        res.append(f'({free} мест)')

    return ' '.join(res)

  @grist.formulaType(grist.Bool())
  def closed(rec, table):
    return rec.status in ('Закрыто', 'Ушёл') or (rec.status == 'До лимита' and rec.count >= rec.limit)

  @grist.formulaType(grist.ReferenceList('Bus_passenger_yearly'))
  def passengers(rec, table):
    return list(Bus_passenger_yearly.lookupRecords(day_to_fest=rec.id,status='Всё верно')) + list(Bus_passenger_yearly.lookupRecords(day_from_fest=rec.id,status='Всё верно')) 

  def count(rec, table):
    return len(rec.passengers) + \
    len(Bus_passenger_yearly.lookupRecords(day_to_fest=rec.id,status='Ждём данных')
    ) + \
    len(Bus_passenger_yearly.lookupRecords(day_from_fest=rec.id,status='Ждём данных')) 

  def undistributed(rec, table):
    return len(Bus_passenger_yearly.lookupRecords(day_to_fest=rec.id,status='Всё верно',bus_to_fest=None)
    ) + \
    len(Bus_passenger_yearly.lookupRecords(day_from_fest=rec.id,status='Всё верно',bus_from_fest=None)) 


@grist.UserTable
class Calendar:
  year = grist.Int()
  start_dt = grist.Date()
  end_dt = grist.Date()
  arrival_dt = grist.Date()
  year_start_dt = grist.Date()

  @grist.formulaType(grist.Bool())
  def is_current_year(rec, table):
    return rec.year == Settings.lookupOne().CURRENT_YEAR


@grist.UserTable
class Direction:
  direction_name26 = grist.Text()
  head26 = grist.ReferenceList('People')
  new_helper26 = grist.ReferenceList('People')

  def _default_last_updated_at26(rec, table, value, user):
    return NOW()
  last_updated_at26 = grist.DateTime('Europe/Moscow')

  def _default_last_updated_by26(rec, table, value, user):
    return user.Email
  last_updated_by26 = grist.Text()
  head_curator26 = grist.ReferenceList('People')

  def _default_head_filter(rec, table, value, user):
    return 1
  head_filter = grist.Numeric()
  B = grist.ChoiceList()
  Locations2026 = grist.ReferenceList('Location')

  def _default_direction_location26(rec, table, value, user):
    return Teams.lookupOne(team_name=rec.direction_name26)
  direction_location26 = grist.Reference('Teams')

  def A(rec, table):
    return None

  def head_tg26(rec, table):
    return rec.head26.telegram

  def head_phone26(rec, table):
    return rec.head26.phone

  def head_helper_Telegram26(rec, table):
    return None

  def C(rec, table):
    return None


@grist.UserTable
class Direction_2025:
  direction_name = grist.Text()
  head = grist.ReferenceList('People')
  type_of_direction = grist.Any()
  head_helper = grist.ReferenceList('People')
  head_curator = grist.Reference('People')

  def _default_last_updated_at(rec, table, value, user):
    return NOW()
  last_updated_at = grist.DateTime('Europe/Moscow')

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()
  directions_locations = grist.ReferenceList('Location_2025', reverse_of='directions')
  new_head = grist.ReferenceList('Participation')
  new_helper = grist.ReferenceList('Participation')

  def _default_direction_location(rec, table, value, user):
    return Teams.lookupOne(team_name=rec.direction_name)
  direction_location = grist.Reference('Teams')

  def head_tg(rec, table):
    return rec.head.telegram

  def head_filter(rec, table):
    return None

  def head_phone(rec, table):
    return rec.head.phone

  def head_helper_Telegram(rec, table):
    return rec.head_helper.telegram

  @grist.formulaType(grist.ReferenceList('People'))
  def org_participations(rec, table):
    return Participation.lookupRecords(year=2025,team=rec.direction_location,role_code='ORGANIZER').person


@grist.UserTable
class HR_roadmap2025:
  HR_ = grist.Text()
  B = grist.Text()
  C = grist.Text()
  D = grist.Text()
  E = grist.Text()
  F = grist.Text()
  G = grist.Text()
  H = grist.Text()
  HR = grist.ReferenceList('People')
  A = grist.Reference('Teams')

  def HR_Telegram(rec, table):
    return rec.HR.telegram


@grist.UserTable
class Import_purgatory_yearly:

  def _default_title(rec, table, value, user):
    if rec.person_id and not value:
      return rec.person.name
    return value.strip() if value else value
  title = grist.Text()

  def _default_role(rec, table, value, user):
    if value:
        return Roles.lookupOne(Code=value)
    elif rec.role_code:
        return Roles.lookupOne(Code=rec.role_code)
    else:
        return Roles.lookupOne(Code="VOLUNTEER")
  role = grist.Reference('Roles')
  position = grist.Text()
  filename = grist.Text()

  def _default_last_name(rec, table, value, user):
    if rec.person_id and not value:
      return rec.person.last_name
    return value.strip() if value else value
  last_name = grist.Text()

  def _default_first_name(rec, table, value, user):
    if rec.person_id and not value:
      return rec.person.first_name
    return value.strip() if value else value
  first_name = grist.Text()

  def _default_gender(rec, table, value, user):
    if rec.person_id and not value:
      return People.lookupOne(id=rec.person_id).gender
    return value.strip() if value else value
  gender = grist.Choice()
  infant = grist.Bool()

  def _default_phone(rec, table, value, user):
    if rec.person_id and not value:
      return "+7" + rec.person.phone_norm_TF[0]

    return value
  phone = grist.Text()

  def _default_parent(rec, table, value, user):
    if rec.parent_id and not value:
      return People.lookupOne(id=rec.parent_id).name
    return value.strip() if value else value
  parent = grist.Text()
  vegan = grist.Bool()

  def _default_telegram(rec, table, value, user):
    if rec.person_id and not value:
        return "@" + rec.person.telegram_norm_TF

    return value
  telegram = grist.Text()

  def _default_birthday(rec, table, value, user):
    return rec.person.birth_date if rec.person_id and not value else value
  birthday = grist.Date()

  def _default_feed_type(rec, table, value, user):
    return 'Ребёнок' if rec.infant_age and rec.infant_age < 16 else value
  feed_type = grist.Choice()
  comment = grist.Text()
  photo_upload = grist.Attachments()
  arrival_date = grist.Date()
  departure_date = grist.Date()
  arrival_transport = grist.Choice()
  departure_transport = grist.Choice()

  def _default_city(rec, table, value, user):
    if rec.person_id and not value:
      return rec.person.city
    return value.strip() if value else value
  city = grist.Text()
  sn = grist.Text()
  document = grist.Text()

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()
  done = grist.Bool()

  def _default_email(rec, table, value, user):
    if rec.person_id and not value:
      return rec.person.email_norm_TF

    return value
  email = grist.Text()
  pasp_agree = grist.Bool()
  curator_code = grist.Text()
  car_model = grist.Text()
  car_color = grist.Choice()
  car_number = grist.Text()
  med_info = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')
  person_id = grist.Int()
  parent_id = grist.Int()

  def _default_updated_by(rec, table, value, user):
    return user.Email
  updated_by = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')
  role_code = grist.Text()

  def _default_batch(rec, table, value, user):
    return Import_series_yearly.lookupOne(folder_name=rec.curator_code)
  batch = grist.Reference('Import_series_yearly')

  def _default_team(rec, table, value, user):
    return [rec.batch.team]
  team = grist.Reference('Teams')

  @grist.formulaType(grist.Text())
  def phone_norm_TF(rec, table):
    s=''.join(filter(str.isnumeric,rec.phone))
    # полагаем что ввели российский мобильный телефон
    # ему соответствует +7 или 8 в начале, а затем 9
    if len(s)==10 and s[0] == '9':
      return s
    elif len(s)==11 and s[0] in '78':
      return s[1:]
    return None

  @grist.formulaType(grist.Bool())
  def is_phone_norm_error(rec, table):
    if rec.phone and rec.phone_norm_TF:
      return False
    else:
      return True


  @grist.formulaType(grist.Text())
  def telegram_norm_TF(rec, table):
    return IFERROR(lambda: (re.search(r"(?:(?<!\S)@|(?:(?:https?://)?(?:t\.me|telegram\.(?:me|dog))/|tg://resolve\?domain=)|(?=\b(?!\w*__)(?!\w*_{2,})(?:[a-z][a-z0-9_]{3,31})(?<!_)\.t\.me$))(?P<username>(?!\w*_{2,})(?!\w*[^0-9a-z_.,\s])(?:[a-z][a-z0-9_]{3,31})(?<!_)\b)(?:\.t\.me)?", rec.telegram.lower(), re.MULTILINE | re.VERBOSE).group(1)),"")

  @grist.formulaType(grist.ReferenceList('People'))
  def people_list(rec, table):
    ts, ps, ns,es = set(), set(), set(), set()
    if rec.telegram_norm_TF:
      ts = {t for t in People.lookupRecords(telegram_norm_TF=rec.telegram_norm_TF )}
    if rec.phone_norm_TF:
      ps = {p for p in People.lookupRecords(phone_norm_TF = CONTAINS(rec.phone_norm_TF) )}
    if len(rec.last_name.strip()) > 1 and len(rec.first_name.strip()) >1:
      ns = {n for n in People.lookupRecords(last_name=rec.last_name.strip(), first_name=rec.first_name.strip() )}
    if rec.email:
      es = {e for e in People.lookupRecords(emailList = CONTAINS(rec.email.lower()) )}

    return set().union(ts,ps,ns,es)

  @grist.formulaType(grist.Text())
  def mapping_state(rec, table):
    if (rec.telegram or rec.phone or rec.last_name):
      state = 'Ч:'+str(len(rec.people_list))
    else:
      state = 'Ч:?'
  
    if (rec.phone or rec.last_name):
      state += ' Б:'+str(len(rec.badge_list))
    else:
      state += ' Б:?'
    return state

  @grist.formulaType(grist.ReferenceList('Badges_2025'))
  def parent_badge_list(rec, table):
    ns = []
    if rec.parent:
      ns = [t for t in Badges_2025.lookupRecords(name=rec.parent.strip())]
  
    return ns

  def full_name(rec, table):
    if (rec.last_name and rec.first_name):
      return rec.last_name + ' ' + rec.first_name  
    else: return rec.title

  @grist.formulaType(grist.Reference('People'))
  def person(rec, table):
    return People.lookupOne(id=rec.person_id)

  def phone_clean(rec, table):
    # Храним значение которое ввели через анкету неизменным.
    # Тут формируем значение которое удобно будет копипастить в Обработке данных.
    # Если анкету заполняли по ссылке из Человеков, Участия данные о Человеке подтягиваем:
    if rec.person_id and not rec.phone:
      return "+7" + rec.person.phone_norm_TF[0]

    # На всякий случай чтобы не было ошибок если ничего не ввели:
    if not rec.phone:
      return rec.phone

    # Для копипаста тут очищаем значение, если получается. Если не получается - оставляем как есть.
    raw = rec.phone.strip()
    digits = ''.join(c for c in raw if c.isdigit())
    if (len(digits) == 10 and digits[0] == '9'):
      result = '+7' + digits
    elif (len(digits) == 11 and digits[0] in '78'):
      result = '+7' + digits[1:]
    else:
      result = raw

    return result

  @grist.formulaType(grist.Text())
  def telegram_clean(rec, table):
    # Храним значение которое ввели через анкету неизменным.
    # Тут формируем значение которое удобно будет копипастить в Обработке данных.
    # Если анкету заполняли по ссылке из Человеков, Участия данные о Человеке подтягиваем:
    if rec.person_id and not rec.telegram:
        return "@" + rec.person.telegram_norm_TF

    # На всякий случай чтобы не было ошибок если ничего не ввели:
    if not rec.telegram:
        return rec.telegram

    # Для копипаста тут очищаем значение, если получается. Если не получается - оставляем как есть.
    result = rec.telegram.strip().lower().replace('https://t.me/', '@')
    if not result.startswith('@'):
        result = '@' + result

    return result

  def document_clean(rec, table):
    # Храним значение которое ввели через анкету неизменным.
    # Тут формируем значение которое удобно будет копипастить в Обработке данных.
    # Для удобства делим серию и номер документа - xxxx yyyyyy, если это предположительно паспорт или св. о рождении.
    if not rec.document:
        return rec.document

    raw = rec.document.strip()
    # Удаляем все пробелы только для проверки формата
    clean = raw.replace(' ', '')

    # Если осталось ровно 10 цифр → это паспорт РФ, форматируем стандартно
    if len(clean) == 10 and clean.isdigit():
        result = clean[:4] + ' ' + clean[4:]
    else:
      # Для остальных документов (с дефисами, буквами, разным количеством пробелов)
      # просто нормализуем пробелы: убираем лишние, оставляем по одному
        result = ' '.join(raw.split())

    return result

  @grist.formulaType(grist.Int())
  def infant_age(rec, table):
    from datetime import date

    adult = 18
    age = adult
    if rec.birthday and rec.arrival_date:
        target_date = rec.arrival_date
        age = target_date.year - rec.birthday.year - ((target_date.month, target_date.day) < (rec.birthday.month, rec.birthday.day))
    
    return age if age < adult else None

  @grist.formulaType(grist.ReferenceList('Badge_yearly'))
  def badge_list(rec, table):
    ns, ps = set(), set()
    if rec.phone_norm_TF:
      ps = {p for p in Badge_yearly.lookupRecords(phone_norm_TF = CONTAINS(rec.phone_norm_TF) )}
    if len(rec.last_name.strip()) > 1 and len(rec.first_name.strip()) >1:
      ns = {t for t in Badge_yearly.lookupRecords(last_name=rec.last_name.strip(), first_name=rec.first_name.strip() )}
  
    return set().union(ns,ps)

  @grist.formulaType(grist.Reference('Badges_2025'))
  def single_badge(rec, table):
    res = Badge_yearly.lookupRecords(
      last_name=rec.last_name.strip(),
      first_name=rec.first_name.strip(),
      str_source=rec.title,
      phone=rec.phone)
    if len(res) == 1 and not Arrival_yearly.lookupRecords(badge=res[0]):
      return res[0]


@grist.UserTable
class Import_series_yearly:
  comment = grist.Text()
  photo_folder = grist.Text()

  def _default_Created_by(rec, table, value, user):
    return user.Name
  Created_by = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_title(rec, table, value, user):
    return rec.team.team_name
  title = grist.Text()

  def _default_folder_name(rec, table, value, user):
    return f"batch{rec.id}"
  folder_name = grist.Text()

  def _default_created_by2(rec, table, value, user):
    return user.Email
  created_by2 = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_updated_dt(rec, table, value, user):
    return user.Email
  updated_dt = grist.Text()
  team = grist.Reference('Teams')

  @grist.formulaType(grist.Text())
  def form_link(rec, table):
    from urllib.parse import urlencode

    # ссылка на Форма доп.анкеты
    url = f"https://grist.insomniafest.ru/forms/qC7y5WLubPsxNuj1UMcLTV/231"

    if rec.folder_name:
    	curator_code = urlencode({'curator_code': rec.folder_name})
    	url += f"?{curator_code}"

    return url


@grist.UserTable
class Lib:

  def GLOBAL_LIBS(rec, table):
    import builtins
    from urllib.parse import urlencode

    # Регистрируем функцию в глобальном пространстве Grist
    builtins.urlencode = urlencode

    # Возвращаем пустоту, чтобы ячейка оставалась чистой
    return "Глобальные библиотеки загружены"

  def get_arrival_bar(rec, table):
    from datetime import date

    def get_arrival_bar(arrival_days, start_day, end_day, month, year=None):
      # arrival_days - это список списков [['2026-06-15', '2026-06-16'], ['2026-07-09', '2026-07-10']]
      # Проверка: если записей заездов нет, возвращаем пустоту
        # Проверка: если записей заездов нет, возвращаем пустоту
        if not arrival_days:
            return None

        if not year:
            year = int(Settings.lookupOne().CURRENT_YEAR)

        # Генерируем список дат для проверяемого диапазона
        target_days = [date(year, month, d) for d in range(start_day, end_day + 1)]

        # Собираем реальные даты присутствия человека
        person_dates = {r for sublist in arrival_days for r in sublist if r}

        # Если заезды человека вообще не пересекаются с этим интервалом, возвращаем None
        if not person_dates.intersection(target_days):
            return None

        # Специальный пробел, равный по ширине одной цифре
        digit_space = "\u2007"

        # Строим шкалу из квадратиков
        result = []
        for day in target_days:
            day_str = f"{day.day:02d}"  # Делает дату двухзначной (например, "01")

            if day in person_dates:
                # Суббота (6) и Воскресенье (7) — желтый, будни — зеленый
                color_box = "🟨" if day.isoweekday() in (6, 7) else "🟩"
                result.append(f"{color_box}{day_str}")
            else:
                # Если человека нет в этот день
                result.append(f"⬜{digit_space}{digit_space}")

        return " ".join(result)

    return get_arrival_bar

  def get_markdown_links(rec, table):
    from urllib.parse import urlencode

    # Функция теперь принимает person и необязательные параметры
    def generate_links(person, role_code="VOLONTEER", position="Волонтёр", curator_code=None):
        # Базовая проверка на существование человека
        if not person or person.to_delete or not person.name:
            return ''

        # Ссылки на формы
        form_link_plusone_adult = "https://grist.insomniafest.ru/forms/q1aBVdSZQJEgJvRXeDa2QD/362"
        form_link_plusone_kid = "https://grist.insomniafest.ru/forms/rnQJgqESTa2a8fWfeiPob1/376"
        form_link_additional_blank = "https://grist.insomniafest.ru/forms/qC7y5WLubPsxNuj1UMcLTV/231"

        # Если curator_code не передан, ищем стандартный
        if not curator_code:
            curator_code = Import_series_yearly.lookupOne(title='Человеки').folder_name

        # Предзаполненные параметры
        base_params = {
            "person_id": person.id,
            "curator_code": curator_code
        }

        # 1. Параметры волонтёра
        url_params = base_params.copy()
        url_params["role_code"] = role_code
        url_params["position"] = position
    
        if person.nickname or person.name:
            url_params["title"] = person.nickname or person.name
        if person.city:
            url_params["city"] = person.city
        
        url_volunteer = f"{form_link_additional_blank}?{urlencode(url_params)}"

        # 2. Параметры для +1 взрослого
        url_params = base_params.copy()
        url_params["role_code"] = "FELLOW"
        url_plus1_adult = f"{form_link_plusone_adult}?{urlencode(url_params)}"

        # 3. Параметры для +1 ребёнка
        url_params = base_params.copy()
        url_params["role_code"] = "FELLOW"
        url_params["infant"] = "True"
        url_plus1_kid = f"{form_link_plusone_kid}?{urlencode(url_params)}"

        # Формируем имя с Telegram, если он заполнен
        telegram_suffix = f" ({person.telegram})" if getattr(person, 'telegram', None) else ""

        # Формируем Markdown-текст
        return '\n\n'.join([
            f"Скопируй нужную ссылку и отправь {person.name}{telegram_suffix}",
            f"[для волонтёра]({url_volunteer})",
            f"[для его взрослого +1]({url_plus1_adult})",
            f"[для его ребёнка +1]({url_plus1_kid})"
        ])

    # Возвращаем функцию в систему
    return generate_links


@grist.UserTable
class Link_hr_team:
  comment = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()

  def _default_isdouble(rec, table, value, user):
    return rec.id != Link_hr_team.lookupOne(team=rec.team, partition_hr=rec.partition_hr, sort_by="created_at").id
  isdouble = grist.Bool()
  partition_hr = grist.Reference('Participation')
  team = grist.Reference('Teams')

  def partition_hr_position(rec, table):
    return rec.partition_hr.position

  @grist.formulaType(grist.Text())
  def partition_hr_person_link_to_card(rec, table):
    return rec.partition_hr.person_link_to_card

  @grist.formulaType(grist.Text())
  def partition_hr_role_name(rec, table):
    return rec.partition_hr.role.Name if rec.partition_hr.role_code != 'VOLUNTEER' else None

  def partition_hr_year(rec, table):
    return rec.partition_hr.year

  def partition_hr_status(rec, table):
    return rec.partition_hr.status.status


@grist.UserTable
class Location:
  Location = grist.Text()
  head = grist.ReferenceList('People')
  coordinator = grist.ReferenceList('People')

  def _default_B(rec, table, value, user):
    return NOW()
  B = grist.Text()

  def _default_E(rec, table, value, user):
    return user.Email
  E = grist.Text()
  status = grist.ChoiceList()
  water = grist.ChoiceList()

  def _default_directions(rec, table, value, user):
    return Direction.lookupRecords(Locations2026=CONTAINS(rec.id)).direction_name26
  directions = grist.ReferenceList('Direction')

  def Locations_Insight2026__(rec, table):
    return Location_insight_2026.lookupRecords(A=rec.id).B


@grist.UserTable
class Location_2025:
  Location = grist.Text()
  status = grist.ChoiceList()
  head = grist.ReferenceList('People')
  coordinator = grist.ReferenceList('People')
  I = grist.Date()
  J = grist.Date()
  L = grist.Any()
  M = grist.Any()
  N = grist.ChoiceList()
  P = grist.Any()
  R = grist.Any()
  S = grist.ChoiceList()
  T = grist.Any()
  U = grist.Bool()
  V = grist.ChoiceList()
  Y = grist.Bool()
  Z = grist.Date()
  AA = grist.Date()
  E = grist.Text()
  F = grist.ChoiceList()
  K = grist.Text()
  Q = grist.Reference('People')

  def _default_last_updated_at(rec, table, value, user):
    return NOW()
  last_updated_at = grist.DateTime('Europe/Moscow')

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()
  C = grist.Text()
  D = grist.ChoiceList()
  directions = grist.ReferenceList('Direction_2025', reverse_of='directions_locations')

  def G(rec, table):
    return None

  def B(rec, table):
    return None

  def H(rec, table):
    return T25_.lookupRecords(A=rec.id).B

  def T25___2(rec, table):
    return T25_.lookupRecords(A=rec.id).C

  def T25___3(rec, table):
    return T25_.lookupRecords(A=rec.id).D

  def T25___(rec, table):
    return T25_.lookupRecords(A=rec.id).E

  @grist.formulaType(grist.Reference('People'))
  def O(rec, table):
    return 0

  @grist.formulaType(grist.ReferenceList('People'))
  def A(rec, table):
    return None

  def W(rec, table):
    return None

  def Locations_description__(rec, table):
    return Location_description.lookupRecords(A=rec.id).B


@grist.UserTable
class Location_25_waterorder:
  B = grist.Numeric()
  C = grist.Numeric()
  D = grist.Text()
  I = grist.Text()
  F = grist.Numeric()
  E = grist.Text()
  A = grist.Reference('Location_2025')


@grist.UserTable
class Location_description:
  B = grist.Text()
  C = grist.Text()
  D = grist.Text()
  E = grist.Text()
  F = grist.ChoiceList()
  G = grist.ChoiceList()
  I = grist.Numeric()
  J = grist.Text()
  Programid = grist.Numeric()
  A = grist.Reference('Location_2025')

  @grist.formulaType(grist.ChoiceList())
  def H(rec, table):
    return rec.A.status

  def directionId(rec, table):
    return None

  def L(rec, table):
    return None

  @grist.formulaType(grist.Bool())
  def K(rec, table):
    return rec.A != "" and rec.A is not None and len(Location_description.lookupRecords(A=rec.A)) > 1


@grist.UserTable
class Location_insight_2026:
  B = grist.Text()
  C = grist.Text()
  D = grist.Text()
  E = grist.Text()
  F = grist.ChoiceList()
  G = grist.ChoiceList()
  I = grist.Numeric()
  J = grist.Text()
  Programid = grist.Numeric()
  A = grist.Reference('Location')

  @grist.formulaType(grist.ChoiceList())
  def status(rec, table):
    return rec.A.status

  def directionId(rec, table):
    return None

  def L(rec, table):
    return None

  @grist.formulaType(grist.Bool())
  def K(rec, table):
    return rec.A != "" and rec.A is not None and len(Location_insight_2026.lookupRecords(A=rec.A)) > 1


@grist.UserTable
class Parking_2025:

  def _default_A(rec, table, value, user):
    if not rec.person: return value
    if (rec.person.last_name and rec.person.first_name):
      return rec.person.last_name + ' ' + rec.person.first_name  
    else: return rec.person.name
  A = grist.Text()
  person = grist.Reference('People')
  B = grist.Text()

  def _default_number(rec, table, value, user):
    return value.replace(' ','')
  number = grist.Text()
  D = grist.Choice()
  E = grist.Choice()

  def _default_F(rec, table, value, user):
    return People.lookupOne(emailList=CONTAINS(rec.Created_by))
  F = grist.Reference('People')
  G = grist.Int()

  def _default_Created_by(rec, table, value, user):
    return user.Email
  Created_by = grist.Text()
  C = grist.Text()

  def _default_role(rec, table, value, user):
    return IFERROR(lambda: (min(filter(lambda r: r.status.color!='red',
      Participation.lookupRecords(person=rec.person,year=2025))
      ,key=lambda r: r.role.priority).role),value_if_error=value) if rec.person else value
  role = grist.Reference('Roles')

  def _default_team_name(rec, table, value, user):
    return IFERROR(lambda: (min(filter(lambda r: r.status.color!='red',
      Participation.lookupRecords(person=rec.person,year=2025))
      ,key=lambda r: r.role.priority).team),value_if_error=value) if rec.person else value
  team_name = grist.Reference('Teams')


@grist.UserTable
class Parking_yearly:
  person = grist.Reference('People')

  def _default_name(rec, table, value, user):
    if not rec.person: return value
    if (rec.person.last_name and rec.person.first_name):
      return rec.person.last_name + ' ' + rec.person.first_name  
    else: return rec.person.name
  name = grist.Text()
  car_model = grist.Text()

  def _default_number(rec, table, value, user):
    return value.replace(' ','')
  number = grist.Text()
  color = grist.Choice()
  E = grist.Choice()

  def _default_coordinator(rec, table, value, user):
    return People.lookupOne(emailList=CONTAINS(rec.created_by))
  coordinator = grist.Reference('People')
  G = grist.Int()

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()
  comment = grist.Text()

  def _default_last_updated_at(rec, table, value, user):
    return NOW()
  last_updated_at = grist.DateTime('Europe/Moscow')

  def _default_role(rec, table, value, user):
    return IFERROR(lambda: (min(filter(lambda r: r.status.color!='red',
      Participation.lookupRecords(person=rec.person,year=2025))
      ,key=lambda r: r.role.priority).role),value_if_error=value) if rec.person else value
  role = grist.Reference('Roles')

  def _default_team_name(rec, table, value, user):
    return IFERROR(lambda: (min(filter(lambda r: r.status.color!='red',
      Participation.lookupRecords(person=rec.person,year=2025))
      ,key=lambda r: r.role.priority).team),value_if_error=value) if rec.person else value
  team_name = grist.Reference('Teams')


@grist.UserTable
class Participation:
  year = grist.Int()
  position = grist.Text()
  mark = grist.Choice()
  notes = grist.Text()
  person_id = grist.Text()
  direction_id = grist.Text()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')
  Row_ID = grist.Numeric()
  person = grist.Reference('People')

  def _default_year_ref(rec, table, value, user):
    return Calendar.lookupOne(is_current_year=True)
  year_ref = grist.Reference('Calendar')

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()
  sub_team = grist.Reference('Sub_team')
  HR_ = grist.Text()
  A = grist.Choice()

  def _default_role(rec, table, value, user):
    return Roles.lookupOne(Code='VOLUNTEER')
  role = grist.Reference('Roles')
  C = grist.Reference('People')

  def _default_reseacher(rec, table, value, user):
    return People.lookupOne(emailList=CONTAINS(user.Email))
  reseacher = grist.Reference('People')
  to_delete = grist.DateTime('Europe/Moscow')

  def _default_UUID(rec, table, value, user):
    return UUID()
  UUID = grist.Text()
  delete_reason = grist.Text()
  arrivals_ref = grist.ReferenceList('Arrival_yearly', reverse_of='engagement')

  def _default_import_serie(rec, table, value, user):
    return Import_series_yearly.lookupOne(team=rec.team, order_by="created_at")
  import_serie = grist.Reference('Import_series_yearly')

  def _default_status(rec, table, value, user):
    return Participation_status.lookupOne(code='PLANNED')
  status = grist.Reference('Participation_status')
  team = grist.Reference('Teams')

  def Telegram2(rec, table):
    return rec.person.telegram

  @grist.formulaType(grist.Int())
  def calendar_year(rec, table):
    return rec.year_ref.year

  def role_code(rec, table):
    return rec.role.Code

  def person_name(rec, table):
    return rec.person.name

  @grist.formulaType(grist.Bool())
  def isHR_Now(rec, table):
    hr=Teams.lookupOne(team_name='HR')
    return True if rec.team==hr and rec.year == YEAR(NOW()) and rec.role.Code in ['VOLUNTEER', 'ORGANIZER', 'VICE', 'TEAM_LEAD'] else False

  def row_id2(rec, table):
    return rec.id

  @grist.formulaType(grist.Int())
  def person_row_id(rec, table):
    return rec.person.id

  @grist.formulaType(grist.Choice())
  def B(rec, table):
    return rec.team.type

  @grist.formulaType(grist.Text())
  def team_name(rec, table):
    return str(rec.year)+"."+ rec.team.team_name +"("+rec.role.Name+")"

  @grist.formulaType(grist.Text())
  def person_link_to_card(rec, table):
    return rec.person.link_to_card

  def status_code(rec, table):
    return rec.status.code

  def status_color(rec, table):
    return rec.status.color

  @grist.formulaType(grist.ReferenceList('Arrivals_2025'))
  def Arrivals_2025(rec, table):
    return Arrivals_2025.lookupRecords(engagement=rec.id)

  @grist.formulaType(grist.Text())
  def participation_page_link(rec, table):
    if rec.year== 2025:
      return f"[{rec.person_name}]({SELF_HYPERLINK(page=35)}#a1.s100.r{rec.id})"
    elif rec.year== 2026:
      return f"[{rec.person_name}]({SELF_HYPERLINK(page=87)}#a1.s274.r{rec.id})"
    else:
      return ''

  @grist.formulaType(grist.Int())
  def order(rec, table):
    if rec.status.color == 'red':
      return 999999999
    if rec.role.Code=='ORGANIZER':
      return 0
    if rec.role.priority > 5 and not rec.sub_team:
      return rec.role.priority * 100000
    r = 0
    if rec.sub_team: r += rec.sub_team.num * 1000
    if rec.role: r += rec.role.priority
    return r

  @grist.formulaType(grist.Bool())
  def is_current_year(rec, table):
    return rec.year==Settings.lookupOne().CURRENT_YEAR

  @grist.formulaType(grist.Text())
  def import_purgatory_form_links(rec, table):
    # 1. Ваши проверки (остаются на стороне таблицы Участие)
    if rec.status_color == 'red':
      return ''
    if rec.to_delete or not rec.person_link_to_card:
      return ''
    if not rec.is_current_year:
      return ''

    # 2. Безопасный сбор данных для аргументов функции
    curator = IFERROR(lambda: (rec.import_serie.folder_name), None)
    pos = IFERROR(lambda: (rec.import_serie.team.name), None) or rec.team.team_name or "Волонтёр"

    # 3. Вызов функции с передачей этих данных
    lib = Lib.lookupOne()
    if lib and lib.get_markdown_links:
        return lib.get_markdown_links(
            person=rec.person, 
            role_code=rec.role.Code, 
            position=pos, 
            curator_code=curator
        )
    return ""

  def arrivals_ref_is_transport_arranged(rec, table):
    return rec.arrivals_ref.is_transport_arranged

  def row_id3(rec, table):
    return rec.id

  def D(rec, table):
    s=set(rec.arrivals_ref.badge)
    if s:
      if len(s) > 1:
        return "Multy!"
      else:
        b = s.pop()
        if b.person == rec.person:
          return "ok"
        elif b.person:
          return b.person.name
        else:
          return b.name
    else:
      return None

  @grist.formulaType(grist.ReferenceList('Badge_yearly'))
  def badge(rec, table):
    return Badge_yearly.lookupRecords(person=rec.person) if rec.person else None


@grist.UserTable
class Participation_status:
  code = grist.Text()
  color = grist.Text()
  icon = grist.Text()
  on_field = grist.Bool()
  use_for = grist.ChoiceList()
  status = grist.Text()
  description = grist.Text()


@grist.UserTable
class People:
  name = grist.Text()

  def _default_last_name(rec, table, value, user):
    return value.strip()
  last_name = grist.Text()

  def _default_first_name(rec, table, value, user):
    return value.strip()
  first_name = grist.Text()
  nickname = grist.Text()
  other_names = grist.Text()
  telegram = grist.Text()
  phone = grist.Text()
  email = grist.Text()
  gender = grist.Choice()
  birth_date = grist.Date()
  vegan = grist.Bool()
  city = grist.Text()
  comment = grist.Text()

  def _default_ntn_id(rec, table, value, user):
    return SUBSTITUTE(UUID(),"-","")
  ntn_id = grist.Text()
  notes = grist.Text()
  matrix_id = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')

  def _default_telegram_norm_TF(rec, table, value, user):
    return IFERROR(lambda: (re.search(r"(?:(?<!\S)@|(?:(?:https?://)?(?:t\.me|telegram\.(?:me|dog))/|tg://resolve\?domain=)|(?=\b(?!\w*__)(?!\w*_{2,})(?:[a-z][a-z0-9_]{3,31})(?<!_)\.t\.me$))(?P<username>(?!\w*_{2,})(?!\w*[^0-9a-z_.,\s])(?:[a-z][a-z0-9_]{3,31})(?<!_)\b)(?:\.t\.me)?", rec.telegram.lower(), re.MULTILINE | re.VERBOSE).group(1)),"")
  telegram_norm_TF = grist.Text()

  def _default_telegram_link(rec, table, value, user):
    return ('https://t.me/'+rec.telegram_norm_TF) if rec.telegram_norm_TF else ''
  telegram_link = grist.Text()

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()
  to_delete = grist.DateTime('Europe/Moscow')

  def _default_editable(rec, table, value, user):
    return True
  editable = grist.Bool()
  delete_reason = grist.Text()

  def emailList(rec, table):
    return rec.email.lower().split()

  def phone_norm_TF(rec, table):
    norm_tels = []
    tlist = rec.phone.split(',')
    for tel in tlist:
      s=''.join(filter(str.isnumeric,tel))
      if len(s)<10:
        pass
      if len(s)==10:
        norm_tels.append(s)
      elif len(s)==11 and s[0] in '78':
        norm_tels.append(s[1:])
    return norm_tels

  @grist.formulaType(grist.Text())
  def email_norm_TF(rec, table):
    return IFERROR(lambda: (re.search(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", rec.email.lower()).group()),"")

  @grist.formulaType(grist.ReferenceList('People'))
  def People_dup(rec, table):
    ts, es, ps = set(), set(), set()
    if rec.telegram_norm_TF:
      ts = {t for t in People.lookupRecords(telegram_norm_TF=rec.telegram_norm_TF ) if t.id!=rec.id}
    if rec.phone_norm_TF:
      for ph in rec.phone_norm_TF:
        ps = set().union(ps, {p for p in People.lookupRecords(phone_norm_TF=CONTAINS(ph)) if p.id!=rec.id } )
    if rec.email_norm_TF:
      es = {e for e in People.lookupRecords(email_norm_TF=rec.email_norm_TF ) if e.id!=rec.id}  
    return set().union(ts,es,ps)

  @grist.formulaType(grist.Text())
  def isInBL(rec, table):
    if Black_list_comment.lookupOne(about_who=rec.id,inBlackList=True):
      return f"[ЧС](https://grist.insomniafest.ru/mhwDM83vLmT3/Insomnia/p/45#a1.s125.r{rec.id})"
    else:
      return "Нет"

  @grist.formulaType(grist.Text())
  def link_to_card(rec, table):
    return f"[{rec.name}]({SELF_HYPERLINK(page=61)}#a1.s173.r{rec.id})"
    #(https://grist.insomniafest.ru/mhwDM83vLmT3/Insomnia/p/61#a1.s173.r{$id})"
    #

  def title(rec, table):
    if rec.telegram_norm_TF:
      return '@' + rec.telegram_norm_TF
    if rec.email_norm_TF:
      return rec.email_norm_TF
    if rec.phone:
      return rec.phone
    return rec.name


  def A(rec, table):
    return SELF_HYPERLINK()

  @grist.formulaType(grist.Text())
  def name_norm(rec, table):
    return ' '.join((rec.name.strip().lower() or "").split())

  @grist.formulaType(grist.Bool())
  def name_double(rec, table):
    return len(People.lookupRecords(name_norm=rec.name_norm)) > 1

  @grist.formulaType(grist.Text())
  def import_purgatory_form_links(rec, table):
    return Lib.lookupOne().get_markdown_links(rec)

  @grist.formulaType(grist.Bool())
  def isHR_Now(rec, table):
    return True if Participation.lookupOne(person=rec.id, isHR_Now = True) else False 

  @grist.formulaType(grist.Bool())
  def isBL_candidat(rec, table):
    ps = Participation.lookupRecords(person=rec.id).mark
    if 'Кандидат в ЧС' in ps:
      return True
    else:
      return False


@grist.UserTable
class Photo:
  person = grist.Reference('People')
  photo = grist.Attachments()
  isForBage = grist.Bool()

  def _default_last_updated_at(rec, table, value, user):
    return NOW()
  last_updated_at = grist.DateTime('Europe/Moscow')

  def _default_Last_updated_by(rec, table, value, user):
    return user.Email
  Last_updated_by = grist.Text()


@grist.UserTable
class Presentation:
  A = grist.Text()
  B = grist.Text()
  C = grist.Text()
  name = grist.Text()


@grist.UserTable
class Problems:
  label = grist.Text()
  description = grist.Text()
  todo = grist.Text()
  link = grist.Text()
  entity = grist.Choice()
  auto = grist.Bool()
  code = grist.Text()


@grist.UserTable
class Questions_FireSafety:
  B = grist.Text()
  C = grist.Bool()
  D = grist.Text()
  E = grist.Bool()
  F = grist.Bool()
  FS_team = grist.Bool()
  fire_home = grist.Choice()
  fire_guests = grist.Choice()
  A = grist.Reference('Location_2025')


@grist.UserTable
class Roadmap_yearly:

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')
  volunteer_recruit_status = grist.Choice()
  volunteer_recruit = grist.Choice()
  age = grist.Choice()
  children = grist.Choice()
  total_cnt = grist.Int()
  arrive_dates = grist.Text()
  skill = grist.Text()
  comment = grist.Text()
  site_status = grist.Choice()
  need_help = grist.Choice()
  take_applications = grist.Choice()
  to_people = grist.Choice()
  feedback_prev_year = grist.Bool()
  recruitment = grist.Choice()
  tg_chat = grist.Choice()
  profi_survey = grist.Bool()
  site_description = grist.Bool()
  chat_readme = grist.Bool()
  lotos = grist.Bool()
  bus_cnt = grist.Int()
  month_ping = grist.Bool()
  list_to_lotos = grist.Bool()
  throw_chat = grist.Bool()

  def _default_last_updated_by(rec, table, value, user):
    return user.Email
  last_updated_by = grist.Text()

  def _default_created_at(rec, table, value, user):
    return NOW()
  created_at = grist.DateTime('Europe/Moscow')
  element_chat = grist.Choice()

  def _default_badge_problem_cnt(rec, table, value, user):
    return len([
      b for b in rec.link_partition_badges
      if b.problem_list
    ])
  badge_problem_cnt = grist.Int()

  def _default_created_by(rec, table, value, user):
    return user.Email
  created_by = grist.Text()

  def _default_year(rec, table, value, user):
    return Calendar.lookupOne(is_current_year=True).year
  year = grist.Reference('Calendar')
  team = grist.Reference('Teams')

  @grist.formulaType(grist.Int())
  def current_cnt(rec, table):
    return len([p for p in rec.link_partitions if p.role_code=='VOLUNTEER' and p.status_color=='green'])

  @grist.formulaType(grist.Int())
  def badge_cnt(rec, table):
    return len(rec.link_partition_badges)

  @grist.formulaType(grist.Int())
  def person_with_arrival_cnt(rec, table):
    return len(set(
        arr.person_id 
        for arr in rec.link_partition_arrivals
    ))

  @grist.formulaType(grist.Int())
  def free_feed_cnt(rec, table):
    return len([
      b for b in rec.link_partition_badges 
      if b.feed_type=='Бесплатно'
    ])

  @grist.formulaType(grist.Int())
  def car_cnt(rec, table):
    return len(Parking_yearly.lookupRecords(team_name=rec.team))

  @grist.formulaType(grist.Numeric())
  def progress(rec, table):
    progress_metrics = [
      rec.volunteer_recruit=='Закрыт', 
      rec.current_cnt>=rec.total_cnt if rec.total_cnt else 0, 
      rec.badge_cnt>=rec.current_cnt,
      rec.person_with_arrival_cnt>=rec.current_cnt,
      rec.need_help!='Хелп!', 
      rec.to_people=='да',
      rec.recruitment=='да',
      rec.tg_chat=='создали',
      rec.feedback_prev_year,
      rec.profi_survey,
      rec.site_description,
      rec.chat_readme,
      rec.month_ping,
      rec.badge_problem_cnt==0,
      rec.arrival_problem_cnt==0,
      rec.list_to_lotos if rec.lotos else True,
      rec.throw_chat,
      rec.no_bus_promo==0
    ]
    progress_no_count = [
        rec.recruitment=='не нужно',
        rec.tg_chat=='не нужно'
    ]
    progress = sum(progress_metrics) / (len(progress_metrics) - sum(progress_no_count))
    return progress

  @grist.formulaType(grist.Numeric())
  def application_form(rec, table):
    year_start_dt = rec.year.year_start_dt
    return len([
            af for af in Application_form.lookupRecords(accepted_team=rec.team) 
            if af.status and af.coordinator 
            and af.created.date() >= year_start_dt
        ])

  @grist.formulaType(grist.Int())
  def arrival_confirmed_cnt(rec, table):
    return len([
      arr for arr in rec.link_partition_arrivals
      if arr.status.A=='Подтверждено накануне' and not arr.problem_list
    ])

  @grist.formulaType(grist.Int())
  def arrival_problem_cnt(rec, table):
    return len([
      arr for arr in rec.link_partition_arrivals
      if arr.status.A=='Подтверждено накануне' 
      and arr.problem_list
    ])

  @grist.formulaType(grist.Bool())
  def isdouble(rec, table):
    return rec.id != Roadmap_yearly.lookupOne(team=rec.team, sort_by="created_at").id

  @grist.formulaType(grist.ReferenceList('Arrival_yearly'))
  def link_partition_arrivals(rec, table):
    return [
        arr for arr in Arrival_yearly.lookupRecords(status_color='green') 
        if arr.engagement in rec.link_partitions
    ]

  @grist.formulaType(grist.Int())
  def no_bus_promo(rec, table):
    return len(Arrival_yearly.lookupRecords(team_ref=rec.team, is_bus=True, bus_promo=None))

  @grist.formulaType(grist.ReferenceList('Badge_yearly'))
  def link_partition_badges(rec, table):
    return [
      b for b in rec.link_partitions.badge
      if b.status in ('Готов к выгрузке', 'Выгружен')
    ]

  @grist.formulaType(grist.ReferenceList('Participation'))
  def link_partitions(rec, table):
    return Participation.lookupRecords(team=rec.team, year=2026)


@grist.UserTable
class Roles:
  Name = grist.Text()
  Color = grist.Text()
  isHead = grist.Bool()
  isFederal = grist.Bool()
  isFeed = grist.Bool()
  Code = grist.Text()
  priority = grist.Numeric()
  need_person = grist.Bool()


@grist.UserTable
class Settings:
  CURRENT_YEAR = grist.Numeric()


@grist.UserTable
class Sub_team:
  name = grist.Text()
  HR = grist.ReferenceList('People')
  archive = grist.Bool()

  def _default_num(rec, table, value, user):
    ref = Sub_team.lookupRecords(team=rec.team)
    if not ref: return 1
    return PEEK(lambda: (MAX(ref.num))) +1
  num = grist.Int()
  team = grist.Reference('Teams')


@grist.UserTable
class T2024:
  A = grist.Text()
  B = grist.Text()
  C = grist.Text()
  D = grist.Text()
  E = grist.Text()
  G = grist.Text()
  H = grist.Text()
  F = grist.Text()
  I = grist.Text()
  J = grist.Text()


@grist.UserTable
class T2025:

  def A(rec, table):
    return None

  def B(rec, table):
    return None

  def C(rec, table):
    return None


@grist.UserTable
class T2026:
  A = grist.Text()
  B = grist.Text()
  C = grist.Text()


@grist.UserTable
class T25_:
  B = grist.Text()
  C = grist.Text()
  D = grist.Text()
  E = grist.Text()
  A = grist.Reference('Location_2025')


@grist.UserTable
class T25_2:

  def D(rec, table):
    return None

  def B(rec, table):
    return None

  def C(rec, table):
    return None

  @grist.formulaType(grist.Reference('Location_2025'))
  def A(rec, table):
    return 0


@grist.UserTable
class Table5:

  def A(rec, table):
    return None

  def B(rec, table):
    return None

  def C(rec, table):
    return None


@grist.UserTable
class Table6:
  A = grist.ReferenceList('Location_2025')
  E = grist.ReferenceList('Location_2025')

  def B(rec, table):
    return None

  def C(rec, table):
    return None

  def D(rec, table):
    return None


@grist.UserTable
class Table7:

  def A(rec, table):
    return None

  def B(rec, table):
    return None

  def C(rec, table):
    return None


@grist.UserTable
class Table8:

  def A(rec, table):
    return None

  def B(rec, table):
    return None

  def C(rec, table):
    return None


@grist.UserTable
class Table9:

  def A(rec, table):
    return None

  def B(rec, table):
    return None

  def C(rec, table):
    return None


@grist.UserTable
class Teams:
  team_name = grist.Text()
  type_of_team = grist.Choice()
  year_of_establishment_ = grist.Numeric()
  last_year = grist.Numeric()
  recruitment = grist.Bool()

  def _default_UUID(rec, table, value, user):
    return UUID()
  UUID = grist.Text()
  type = grist.Choice()

  def _default_updated_at(rec, table, value, user):
    return NOW()
  updated_at = grist.DateTime('Europe/Moscow')
  to_delete = grist.DateTime('Europe/Moscow')

  def _default_name_for_badge(rec, table, value, user):
    return value if len(value) <=20 else value[:20]
  name_for_badge = grist.Text()
  parent = grist.Reference('Teams', reverse_of='child')
  child = grist.ReferenceList('Teams', reverse_of='parent')

  @grist.formulaType(grist.Bool())
  def is2025(rec, table):
    return True if rec.type != "Грантовое" and rec.type_of_team != "Коммерческая локация" and rec.type_of_team != "Зона ответственности" and rec.last_year ==0  else False

  @grist.formulaType(grist.Text())
  def delete_reason(rec, table):
    return ''


@grist.UserTable
class Technical_section:
  A = grist.Text()
  B = grist.Text()
  C = grist.Text()


@grist.UserTable
class Tickets:
  number = grist.Text()
  link = grist.Text()
  series = grist.Numeric()

  def _default_issued_at(rec, table, value, user):
    return NOW() if rec.badges_2025_ref or rec.issued_without_badge else None
  issued_at = grist.DateTime('Europe/Moscow')
  issued_without_badge = grist.Bool()
  to_delete = grist.Bool()
  comment = grist.Text()

  def _default_issued_by(rec, table, value, user):
    return user.Email if rec.badges_2025_ref or rec.issued_without_badge else None
  issued_by = grist.Text()
  badges_2025_ref = grist.Reference('Badge_yearly', reverse_of='tickets_ref')
