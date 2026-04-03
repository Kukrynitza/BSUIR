# SPARQL-запросы для pbz-lab-2

---

## Структура данных

### pbz-lab-2.owx (наша онтология)

**OGMS экземпляры — наши данные (тип OGMS_0000031 — disease):**
| Экземпляр | severityLevel | diseaseCode | patientName |
|---|---|---|---|
| Disease_Appendicitis | High | K35.8 | Kozlov |
| Disease_Hernia | Medium | K40.9 | Sidorov |
| Disease_Pneumonia | High | J18.9 | Petrov |

**OGMS экземпляры — данные из OGMS (добавлены в наш файл):**
| Экземпляр | treatmentDurationDays | symptoms |
|---|---|---|
| OGMS_Appendicitis | 45 | abdominal pain, fever, nausea |
| OGMS_Hernia | 30 | bulging, discomfort |
| OGMS_Pneumonia | 60 | cough, fever, chest pain |

**COB экземпляры — процедуры (тип COB_0000082 — planned process):**
| Экземпляр | label | procedureDuration | usesDevice | hasInput |
|---|---|---|---|---|
| COB_Appendectomy | Surgery_Appendectomy_01 | 45 | COB_Scalpel | COB_Appendix |
| COB_Hernioplasty | Surgery_Hernioplasty_02 | 60 | — | COB_Heart |

**COB экземпляры — устройства (тип COB_00001300 — device):**
| Экземпляр | label | deviceModel | deviceMaterial |
|---|---|---|---|
| COB_Scalpel | Scalpel_Disposable_15 | Scalpel-200 | Stainless Steel |

**COB экземпляры — органы (тип BFO_0000040 — material entity):**
| Экземпляр | label | organName |
|---|---|---|
| COB_Appendix | Organ_Appendix_Human | Appendix |
| COB_Heart | Organ_Heart_Human | Heart |

### Принцип JOIN
Две онтологии независимы. SPARQL объединяет данные через `?label` (одинаковый rdfs:label) для OGMS и через объектные свойства + label для COB.

---

# ===== OGMS ЗАПРОСЫ (4 шт) =====

---

## Запрос OGMS-1: Заболевания с длительным лечением и их коды

**Что делает:** Находит заболевания, которые лечатся больше 40 дней, и показывает их ICD-10 коды и симптомы. JOIN двух онтологий — наша даёт код, OGMS даёт лечение.

**Как работает:**
1. SPARQL находит `Disease_Appendicitis` в нашей онтологии → берёт `diseaseCode = "K35.8"`
2. Ищет экземпляр в OGMS с ТЕМ ЖЕ label `"Appendicitis"` → находит `OGMS_Appendicitis`
3. Берёт из OGMS: `treatmentDurationDays = 45`, `symptoms = "abdominal pain, fever, nausea"`
4. FILTER: 45 > 40? Да → строка в результат
5. Pneumonia: J18.9 + 60 дней → проходит
6. Hernia: K40.9 + 30 дней → 30 > 40? Нет → отсеивается

**Кто что дал:**
- Наша онтология → diseaseCode (K35.8, J18.9)
- OGMS → treatmentDurationDays (45, 60), symptoms
- Без одной из онтологий → неполная строка

**Результат:** Appendicitis (K35.8, 45д), Pneumonia (J18.9, 60д)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?label ?code ?treatmentDays ?symptoms WHERE {
    ?ours rdfs:label ?label .
    ?ours obo:diseaseCode ?code .

    ?ogms rdfs:label ?label .
    ?ogms obo:treatmentDurationDays ?treatmentDays .
    ?ogms obo:symptoms ?symptoms .

    FILTER(?treatmentDays > 40)
}
```

---

## Запрос OGMS-2: Пациенты и их заболевания с лечением

**Что делает:** Показывает имена пациентов из нашей онтологии + длительность лечения и симптомы из OGMS. Без нашей онтологии — неизвестно кто болеет. Без OGMS — неизвестно сколько лечат.

**Как работает:**
1. Находит `OGMS_Appendicitis` → treatment=45, symptoms="abdominal pain, fever, nausea"
2. Ищет в нашей онтологии экземпляр с label `"Appendicitis"` → находит `Disease_Appendicitis`
3. Берёт `patientName = "Kozlov"`
4. Объединяет: Kozlov болеет Appendicitis, лечится 45 дней

**Кто что дал:**
- OGMS → treatmentDurationDays, symptoms (медицинские данные)
- Наша онтология → patientName (кто болеет)
- Связь → общий label

**Результат:** 3 строки (Kozlov+Appendicitis+45, Sidorov+Hernia+30, Petrov+Pneumonia+60)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?label ?patient ?treatmentDays ?symptoms WHERE {
    ?ogms rdfs:label ?label .
    ?ogms obo:treatmentDurationDays ?treatmentDays .
    ?ogms obo:symptoms ?symptoms .

    ?ours rdfs:label ?label .
    ?ours obo:patientName ?patient .
}
```

---

## Запрос OGMS-3: Заболевания с тяжёлым течением и длительным лечением

**Что делает:** Находит заболевания с severityLevel из нашей онтологии + лечение > 35 дней из OGMS. Показывает какие тяжёлые заболевания требуют длительного лечения.

**Как работает:**
1. Находим `OGMS_Appendicitis` → 45 дней лечения
2. JOIN по label → наш `Disease_Appendicitis` → severityLevel = "High"
3. FILTER: 45 > 35? Да → строка в результат
4. Hernia: 30 дней → 30 > 35? Нет → отсеивается
5. Pneumonia: 60 дней, severity = "High" → проходит

**Кто что дал:**
- OGMS → treatmentDurationDays (медицинский факт)
- Наша онтология → severityLevel (наша оценка тяжести)
- FILTER по OGMS данным отсеивает лёгкие случаи

**Результат:** Appendicitis (High, 45д), Pneumonia (High, 60д)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?label ?severity ?treatmentDays ?symptoms WHERE {
    ?ogms rdfs:label ?label .
    ?ogms obo:treatmentDurationDays ?treatmentDays .
    ?ogms obo:symptoms ?symptoms .

    ?ours rdfs:label ?label .
    ?ours obo:severityLevel ?severity .

    FILTER(?treatmentDays > 35)
}
```

---

## Запрос OGMS-4: Полная картина заболевания из двух онтологий

**Что делает:** Объединяет ВСЕ свойства из обеих онтологий в одну таблицу. Без фильтров — полная картина. Ни одна онтология не может дать все 5 полей отдельно.

**Как работает:**
1. Для каждого экземпляра с label берём 3 свойства из нашей онтологии
2. Находим OGMS экземпляр с тем же label → берём 2 свойства
3. Объединяем в одну строку

**Кто что дал:**
- Наша онтология (3 столбца): severityLevel, diseaseCode, patientName
- OGMS (2 столбца): treatmentDurationDays, symptoms
- Итого 5 столбцов из 2 независимых онтологий

**Результат:** 3 строки с полной информацией

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?label ?severity ?code ?patient ?treatmentDays ?symptoms WHERE {
    ?ours rdfs:label ?label .
    ?ours obo:severityLevel ?severity .
    ?ours obo:diseaseCode ?code .
    ?ours obo:patientName ?patient .

    ?ogms rdfs:label ?label .
    ?ogms obo:treatmentDurationDays ?treatmentDays .
    ?ogms obo:symptoms ?symptoms .
}
```

---

# ===== COB ЗАПРОСЫ (3 шт) =====

### Структура JOIN (COB):
Наши экземпляры (webprotege:) и COB экземпляры (obo:) имеют **одинаковый label**:
| Наши экземпляры | Label | COB экземпляры | COB свойства |
|---|---|---|---|
| Surgery_Appendectomy_01 | "Surgery_Appendectomy_01" | COB_Appendectomy | procedureDuration=45 |
| Surgery_Hernioplasty_02 | "Surgery_Hernioplasty_02" | COB_Hernioplasty | procedureDuration=60 |
| Scalpel_Disposable_15 | "Scalpel_Disposable_15" | COB_Scalpel | deviceModel, deviceMaterial |
| Organ_Appendix_Human | "Organ_Appendix_Human" | COB_Appendix | organName=Appendix |
| Organ_Heart_Human | "Organ_Heart_Human" | COB_Heart | organName=Heart |

---

## Запрос COB-1: Наши операции + модель инструмента из COB

**Что делает:** Показывает наши хирургические операции и какая модель инструмента используется. Данные приходят из двух онтологий — наша знает что это за операция, COB знает характеристики инструмента.

**Как работает:**
1. `?ours rdfs:label ?label` — находит наши экземпляры (`Surgery_Appendectomy_01`, `Surgery_Hernioplasty_02`) и берёт их label
2. `?cob rdfs:label ?label` — ищет COB экземпляр с ТЕМ ЖЕ label. Находит `COB_Appendectomy` с label `"Surgery_Appendectomy_01"`
3. `?cob obo:procedureDuration ?duration` — из COB экземпляра берёт длительность (45)
4. `?cob obo:usesDevice ?device` — из COB через object property `usesDevice` переходит к `COB_Scalpel`
5. `?device obo:deviceModel ?deviceModel` — из COB берёт модель инструмента ("Scalpel-200")

**Кто что дал:**
- Наша онтология → label операции (`Surgery_Appendectomy_01`). Без нас — COB не знает что за операция
- COB → `procedureDuration` (45), `deviceModel` ("Scalpel-200"). Без COB — мы не знаем длительность и характеристики инструмента
- JOIN → общий label между нашим экземпляром и COB экземпляром

**Результат:** Surgery_Appendectomy_01 (45д, Scalpel-200), Surgery_Hernioplasty_02 (60д)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?label ?duration ?deviceModel WHERE {
    # Наши экземпляры — label
    ?ours rdfs:label ?label .

    # COB экземпляры — duration (JOIN по label)
    ?cob rdfs:label ?label .
    ?cob obo:procedureDuration ?duration .

    OPTIONAL {
        ?cob obo:usesDevice ?device .
        ?device obo:deviceModel ?deviceModel .
    }
}
```

---

## Запрос COB-2: Длительные операции + какой орган оперируется

**Что делает:** Находит операции длиннее 40 минут и показывает какой орган оперируется. Использует COB свойство `has input` (RO_0002233) — стандартное свойство из COB которое связывает процесс с материальным объектом.

**Как работает:**
1. `?proc rdfs:label ?procLabel` — находит COB экземпляр процедуры (`COB_Appendectomy`) и берёт label
2. `?proc obo:procedureDuration ?duration` — берёт длительность (45)
3. `?proc obo:RO_0002233 ?organ` — через COB свойство `has input` (RO_0002233) переходит к органу. Находит `COB_Appendix`
4. `?organ rdfs:label ?organLabel` — берёт label органа (`Organ_Appendix_Human`)
5. `FILTER(?duration > 40)` — оставляет только операции длиннее 40 минут

**Кто что дал:**
- COB → класс `planned process` (COB_0000082), свойство `has input` (RO_0002233), `procedureDuration`. Без COB — нет семантической связи «процедура использует орган»
- Наша онтология → экземпляры операций и органов (обеспечивает label). Без нас — COB не знает что за конкретная операция
- Связь → COB object property `has input` соединяет процедуру с органом

**Результат:** Surgery_Appendectomy_01 (45д, Organ_Appendix_Human), Surgery_Hernioplasty_02 (60д, Organ_Heart_Human)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?procLabel ?duration ?organLabel WHERE {
    # COB: процедура с duration
    ?proc rdfs:label ?procLabel .
    ?proc obo:procedureDuration ?duration .

    # COB: has input → орган
    ?proc obo:RO_0002233 ?organ .
    ?organ rdfs:label ?organLabel .

    FILTER(?duration > 40)
}
```

---

## Запрос COB-3: Операции + инструменты + органы — полная картина

**Что делает:** Объединяет ВСЕ данные: операция → инструмент (через `usesDevice`) → орган (через `has input`). Три типа данных из COB связанных через object properties.

**Как работает:**
1. `?proc rdfs:label ?procLabel` — COB экземпляр процедуры (`COB_Appendectomy`)
2. `?proc obo:procedureDuration ?duration` — 45 минут
3. `?proc obo:usesDevice ?device` — через `usesDevice` → `COB_Scalpel`
4. `?device obo:deviceModel ?deviceModel` — "Scalpel-200"
5. `?device obo:deviceMaterial ?material` — "Stainless Steel"
6. `?proc obo:RO_0002233 ?organ` — через `has input` → `COB_Appendix`
7. `?organ obo:organName ?organName` — "Appendix"

**Кто что дал:**
- COB → 3 класса (`planned process`, `device`, `material entity`) + 2 object property (`usesDevice`, `has input`) + data properties (`deviceModel`, `deviceMaterial`, `organName`, `procedureDuration`). Это **семантическая структура** из COB
- Наша онтология → экземпляры (обеспечивает label). Это **конкретные данные**
- Связь → COB object properties формируют цепочку: процедура → устройство, процедура → орган

**Результат:** Surgery_Appendectomy_01 (45д, Scalpel-200, Stainless Steel, Appendix)

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT ?procLabel ?duration ?deviceModel ?material ?organName WHERE {
    # COB: процедура
    ?proc rdfs:label ?procLabel .
    ?proc obo:procedureDuration ?duration .

    # COB: устройство через usesDevice
    ?proc obo:usesDevice ?device .
    ?device obo:deviceModel ?deviceModel .
    ?device obo:deviceMaterial ?material .

    # COB: орган через has input
    ?proc obo:RO_0002233 ?organ .
    ?organ obo:organName ?organName .
}
```
