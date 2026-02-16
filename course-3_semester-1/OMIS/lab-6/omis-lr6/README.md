
В frontend\omis-lab-6 добавить файл .env с сдедующием содержанием
NEXT_PUBLIC_SUPABASE_URL=https://[какой-то путь].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[GROQ_API_KEY]

В backend/main в client = Groq("api_key=GROQ_API_KEY") вместо GROQ_API_KEY вставить ключ с GROQ


backend запускается из папки командой uvicorn main:app --reload --port 8000

Перед запуском необходимо использовать команду из папки frontend\omis-lab-6 npm install для установки всех необходимых библиотек и связей, в дальшейшем frontend запускается из папки frontend\omis-lab-6 командой npm run dev
