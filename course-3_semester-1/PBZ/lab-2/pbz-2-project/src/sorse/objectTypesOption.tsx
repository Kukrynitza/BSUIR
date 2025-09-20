interface Option {
    value: string;
    label: string;
}

export const objectTypesOption: Option[] = [  
  { value: 'Concert venue', label: 'Концертная площадка' },
  { value: 'Theater', label: 'Театр' },
  { value: 'Cinema', label: 'Кинотеатр' },
  { value: 'Circus', label: 'Цирк' },
  { value: 'Museum', label: 'Музей' },
  { value: 'Art gallery', label: 'Художественная галерея' },
  { value: 'Bowling alley', label: 'Боулинг' },
  { value: 'Billiard club', label: 'Бильярдный клуб' },
  { value: 'Karaoke club', label: 'Караоке-клуб' },
  { value: 'Nightclub', label: 'Ночной клуб' },
  { value: 'Dance club', label: 'Танцевальный клуб' },
  { value: 'Comedy club', label: 'Комедийный клуб' },
  { value: 'Concert hall', label: 'Концертный зал' },
  { value: 'Opera house', label: 'Оперный театр' },
  { value: 'Philharmonic', label: 'Филармония' },
  { value: 'Exhibition center', label: 'Выставочный центр' },
  { value: 'Amusement park', label: 'Парк развлечений' },
  { value: 'Water park', label: 'Аквапарк' },
  { value: 'Zoo', label: 'Зоопарк' },
  { value: 'Aquarium', label: 'Океанариум' },
  { value: 'Planetarium', label: 'Планетарий' }
]