18
SELECT "Д#"
FROM "S"
WHERE "S" > 320
GROUP BY "Д#"

25
WITH "sity_1" as(
SELECT "Город"
FROM "Проекты J"
ORDER BY "Город" ASC
LIMIT 1

)

SELECT  "Имя ПР", "Город"
FROM "Проекты J"
WHERE "Город" IN (SELECT * FROM "sity_1")
ORDER BY "Город" ASC


33
SELECT "Проекты J"."Город"
FROM "Проекты J" 
GROUP BY "Проекты J"."Город"
union
SELECT "Поставщики S"."Город"
FROM "Поставщики S"
GROUP BY "Поставщики S"."Город"
union
SELECT "Детали P"."Город"
FROM "Детали P"
GROUP BY "Детали P"."Город"

13
SELECT "S"."П#"
FROM "S" INNER JOIN "Проекты J" ON "S"."ПР#" = "Проекты J"."ПР#"
INNER JOIN "Поставщики S" ON "S"."П#" = "Поставщики S"."П#"
WHERE "Поставщики S"."Город" != "Проекты J"."Город"
GROUP BY "S"."П#"

35
SELECT "Поставщики S"."П#", "Детали P"."Д#"
FROM "Поставщики S" CROSS JOIN "Детали P"
except
SELECT "S"."П#", "S"."Д#"
FROM "S"

15
SELECT COUNT("ПР#")
FROM "S"
WHERE "S"."П#" = 'П1'

19
SELECT "Проекты J"."Имя ПР"
FROM "S" INNER JOIN "Проекты J" ON "S"."ПР#" = "Проекты J"."ПР#"
WHERE "S"."П#" = 'П1'
GROUP BY "Проекты J"."Имя ПР"

29
WITH "table_1" as (SELECT "ПР#"
FROM "S"
WHERE "S"."П#" like 'П1'
GROUP BY "ПР#"
)

SELECT "ПР#"
FROM "table_1"
except
SELECT "S"."ПР#"
FROM "table_1" inner JOIN "S" ON "table_1"."ПР#" = "S"."ПР#"
WHERE "S"."П#" != 'П1'
GROUP BY "S"."ПР#"

20
SELECT "Детали P"."Цвет"
FROM "S" INNER JOIN "Детали P" ON "S"."Д#" = "Детали P"."Д#"
WHERE "S"."П#" = 'П1'
group BY "Детали P"."Цвет"

21
SELECT "Детали P"."Цвет"
FROM "S" INNER JOIN "Проекты J" ON "S"."ПР#" = "Проекты J"."ПР#"
INNER JOIN "Детали P" ON "S"."Д#" = "Детали P"."Д#"
WHERE "Проекты J"."Город" = 'Лондон'
GROUP BY "Детали P"."Цвет"