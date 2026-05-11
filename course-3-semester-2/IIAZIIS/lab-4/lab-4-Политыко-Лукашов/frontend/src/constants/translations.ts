export const ENTITY_TRANSLATIONS: Record<string, string> = {
  'Object': 'Объект',
  'Entity': 'Сущность',
  'Event': 'Событие',
  'Property': 'Свойство',
  'Quantity': 'Количество',
  'Manner': 'Образ действия',
  'FunctionWord': 'Служебное слово',
  'Punctuation': 'Пунктуация',
  'Participant': 'Участник',
};

export const ROLE_TRANSLATIONS: Record<string, string> = {
  'Agent': 'Агент (субъект)',
  'Patient': 'Пациент (объект)',
  'Predicate': 'Предикат',
  'Attribute': 'Атрибут',
  'Circumstance': 'Обстоятельство',
  'EventCore': 'Ядро события',
  'Participant': 'Участник',
  'FunctionWord': 'категория (часть речи)',
};

export function translateEntity(entity: string): string {
  return ENTITY_TRANSLATIONS[entity] || entity;
}

export function translateRole(role: string): string {
  return ROLE_TRANSLATIONS[role] || role;
}
