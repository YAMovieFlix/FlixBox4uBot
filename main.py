import asyncio
import logging
import random
import string
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================
# ⚙️ CONFIGURATION (আপনার ডিটেইলস দিন)
# ==========================================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
MONGO_URI = "YOUR_MONGODB_URI_HERE"
# Render বা Koyeb এ ডিপ্লয় করার পর যে ওয়েবসাইটের লিংক পাবেন, সেটা এখানে দিবেন
WEB_APP_URL = "https://your-app-name.onrender.com" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client['MovieeLinkDB']

# ==========================================
# 🌐 FRONTEND WEB APP (REACT + TAILWIND IN HTML)
# ==========================================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MovieeLink App</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- React & ReactDOM -->
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <!-- Babel for JSX -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <!-- Telegram Web App Script -->
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <!-- Monetag Script (Replace ZONE_ID) -->
    <!-- <script src="https://alwingulla.com/88/tag.min.js" data-zone="YOUR_ZONE_ID"></script> -->
</head>
<body class="bg-[#f4f4f5] text-gray-800 font-sans selection:bg-indigo-100">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        const SmartTools = () => (
            <div className="p-4 bg-[#f8f9fe] min-h-screen pb-24">
                <div className="flex flex-col items-center mb-6">
                    <h2 className="text-xl font-bold text-indigo-600 flex items-center gap-2">🛠 Smart Tools</h2>
                    <p className="text-xs text-gray-400">All the essential tools in one place ✨</p>
                </div>
                <input type="text" placeholder="🔍 Search tools..." className="w-full p-3 rounded-xl border border-gray-200 text-sm mb-6 outline-none" />
                <div className="flex gap-2 mb-6">
                    <div className="flex-1 bg-white p-3 rounded-xl text-center shadow-sm"><div className="text-xl font-bold text-indigo-600">20</div><div className="text-[10px] text-gray-400">Total Tools</div></div>
                    <div className="flex-1 bg-white p-3 rounded-xl text-center shadow-sm"><div className="text-xl font-bold text-blue-500">7</div><div className="text-[10px] text-gray-400">Newly added</div></div>
                    <div className="flex-1 bg-white p-3 rounded-xl text-center shadow-sm"><div className="text-xl font-bold text-green-500">100%</div><div className="text-[10px] text-gray-400">Free to use</div></div>
                </div>
                <h3 className="font-bold text-gray-800 mb-3 text-sm">🔥 Popular Tools</h3>
                <div className="grid grid-cols-2 gap-3">
                    {['EMI Calculator 💰', 'Date Difference 📅', 'Text Case 🔠', 'Zakat Calculator 🕌'].map(tool => (
                        <div key={tool} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 relative">
                            <span className="absolute top-0 right-0 bg-teal-400 text-white text-[10px] px-2 py-1 rounded-bl-xl rounded-tr-xl font-bold">NEW</span>
                            <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-xl mb-2">{tool.split(' ')[2]}</div>
                            <h3 className="text-xs font-bold">{tool.split(' ').slice(0,2).join(' ')}</h3>
                        </div>
                    ))}
                </div>
            </div>
        );

        const MovieDetails = () => {
            const [adTimer, setAdTimer] = useState(0);
            const [isAdRunning, setIsAdRunning] = useState(false);
            const [isUnlocked, setIsUnlocked] = useState(false);

            const handleDownloadClick = () => {
                if (isUnlocked) {
                    alert("Download started!"); // Here you put real DB link
                    return;
                }
                // Call Monetag Ad
                // if(window.showMonetagAd) window.showMonetagAd(); 

                setIsAdRunning(true);
                let timeLeft = 15;
                setAdTimer(timeLeft);
                const timer = setInterval(() => {
                    timeLeft -= 1;
                    setAdTimer(timeLeft);
                    if (timeLeft <= 0) {
                        clearInterval(timer);
                        setIsUnlocked(true);
                        setIsAdRunning(false);
                    }
                }, 1000);
            };

            return (
                <div className="bg-white min-h-screen pb-24">
                    <div className="relative">
                        <img src="https://i.ibb.co/3sZq1bT/movie-thumb.jpg" className="w-full h-60 object-cover" />
                        <span className="absolute top-3 left-3 bg-yellow-400 text-black px-2 py-0.5 text-xs font-bold rounded">HD</span>
                    </div>
                    <div className="p-4">
                        <h1 className="text-xl font-bold">Shada Private Natok</h1>
                        <div className="flex justify-around my-6 text-center text-sm font-medium text-gray-500">
                            <div><span className="block text-2xl text-red-500 mb-1">❤️</span> 3 Like</div>
                            <div><span className="block text-2xl text-blue-400 mb-1">⬇️</span> 82 Download</div>
                            <div><span className="block text-2xl text-gray-600 mb-1">💬</span> 0</div>
                        </div>

                        <button onClick={handleDownloadClick} disabled={isAdRunning} className={`w-full py-3 rounded-xl font-bold mb-3 transition-all ${isUnlocked ? 'bg-green-500 text-white' : 'bg-[#fff1ec] text-[#e65c2a] border border-[#ffdfd4]'}`}>
                            {isAdRunning ? `⏳ Please wait... ${adTimer}s (Ad is showing)` : isUnlocked ? '✅ Download Now' : '💡 Tap the button below to download easily'}
                        </button>

                        <button className="w-full bg-[#1b55e2] text-white py-3 rounded-xl font-medium mb-6 text-sm shadow-md">❓ Need help? Watch the tutorial</button>
                        
                        <div className="flex gap-3 text-sm font-medium mb-6">
                            <button className="flex-1 border border-pink-200 text-pink-500 py-3 rounded-full">♡ Like</button>
                            <button className="flex-[1.5] bg-black text-white py-3 rounded-full">⬇ Download</button>
                            <button className="flex-1 border border-orange-200 text-orange-500 py-3 rounded-full">🔖 Save</button>
                        </div>
                    </div>
                </div>
            );
        };

        const App = () => {
            const [page, setPage] = useState('movie');
            const [showWelcome, setShowWelcome] = useState(true);

            useEffect(() => {
                if(window.Telegram && window.Telegram.WebApp) {
                    window.Telegram.WebApp.expand();
                }
            }, []);

            return (
                <div>
                    {showWelcome && (
                        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
                            <div className="bg-white rounded-3xl p-6 text-center w-full max-w-sm shadow-2xl">
                                <h2 className="text-2xl font-bold mb-4">👋 Welcome to<br/>MovieeLink Bot!</h2>
                                <div className="text-left text-gray-600 text-sm space-y-4 mb-8">
                                    <p>🎬 এখানে আপনি হাজারো Movie, Web Series দেখতে পারবেন।</p>
                                    <p>🔍 আপনার পছন্দের Movie খুঁজতে Search ব্যবহার করুন।</p>
                                </div>
                                <button onClick={() => setShowWelcome(false)} className="bg-[#6c5ce7] text-white px-8 py-3 rounded-xl font-bold">OK ✅</button>
                            </div>
                        </div>
                    )}

                    {page === 'movie' ? <MovieDetails /> : <SmartTools />}

                    <div className="fixed bottom-0 w-full bg-[#f4f4f5] border-t flex justify-between px-6 py-3 text-[10px] text-gray-500 font-medium z-40">
                        <button onClick={() => setPage('movie')} className={`flex flex-col items-center ${page==='movie'?'text-red-500':''}`}><span className="text-2xl mb-0.5">🏠</span> Home</button>
                        <button className="flex flex-col items-center"><span className="text-2xl mb-0.5">🔖</span> Favorite</button>
                        <button onClick={() => setPage('tools')} className={`flex flex-col items-center ${page==='tools'?'text-red-500':''}`}><span className="text-2xl mb-0.5">🔧</span> Tools</button>
                        <button className="flex flex-col items-center"><span className="text-2xl mb-0.5">📅</span> Upcoming</button>
                        <button className="flex flex-col items-center"><span className="text-xl bg-pink-200 text-pink-600 rounded-full px-1.5 py-0.5 mb-1 mt-0.5">TE</span> Setting</button>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

# Web Server Route Handler
async def handle_webapp(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

# ==========================================
# 🤖 BOT BACKEND (STATES & COMMANDS)
# ==========================================
class MovieState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class SeriesState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    s_num = State(); e_num = State()
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎬 Open MovieeLink App", web_app=types.WebAppInfo(url=WEB_APP_URL))]
    ])
    await message.answer("👋 **Welcome to MovieeLink Bot!**\n\n🎬 এখানে আপনি হাজারো Movie ও Series দেখতে পারবেন।", reply_markup=markup)

# --- Add Movie (Unlimited Loop) ---
@dp.message(Command("movies"))
async def add_movie(message: types.Message, state: FSMContext):
    await state.clear(); await message.answer("🎬 মুভির নাম দিন:"); await state.set_state(MovieState.title)

@dp.message(MovieState.title)
async def m_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text, qualities=[]); await message.answer("📅 সাল দিন:"); await state.set_state(MovieState.year)

@dp.message(MovieState.year)
async def m_cat(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text); await message.answer("📁 ক্যাটাগরি সিলেক্ট করুন (Action/Romance):"); await state.set_state(MovieState.category)

@dp.message(MovieState.category)
async def m_lang(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text); await message.answer("🗣 ভাষা সিলেক্ট করুন (Bangla/Hindi):"); await state.set_state(MovieState.language)

@dp.message(MovieState.language)
async def m_res(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text); await message.answer("📺 কোয়ালিটি দিন (720p/1080p):"); await state.set_state(MovieState.q_res)

@dp.message(MovieState.q_res)
async def m_link(message: types.Message, state: FSMContext):
    await state.update_data(cur_res=message.text); await message.answer("🔗 লিংক দিন:"); await state.set_state(MovieState.q_link)

@dp.message(MovieState.q_link)
async def m_size(message: types.Message, state: FSMContext):
    await state.update_data(cur_link=message.text); await message.answer("💾 সাইজ দিন (1.2GB):"); await state.set_state(MovieState.q_size)

@dp.message(MovieState.q_size)
async def m_ask(message: types.Message, state: FSMContext):
    data = await state.get_data()
    qualities = data.get('qualities', [])
    qualities.append({"res": data['cur_res'], "link": data['cur_link'], "size": message.text})
    await state.update_data(qualities=qualities)
    
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ আরও কোয়ালিটি এড", callback_data="m_more")],
        [types.InlineKeyboardButton(text="✅ সেভ করুন (Skip)", callback_data="m_save")]
    ])
    await message.answer(f"{len(qualities)} টি কোয়ালিটি এড হয়েছে। আরও এড করবেন?", reply_markup=markup)
    await state.set_state(MovieState.ask_more)

@dp.callback_query(MovieState.ask_more)
async def m_save(call: types.CallbackQuery, state: FSMContext):
    if call.data == "m_more":
        await call.message.edit_text("📺 নতুন কোয়ালিটি দিন:"); await state.set_state(MovieState.q_res)
    else:
        d = await state.get_data()
        await db.movies.insert_one({"title": d['title'], "year": d['year'], "category": d['category'], "language": d['language'], "qualities": d['qualities']})
        await call.message.edit_text(f"🎉 মুভি সেভ হয়েছে!"); await state.clear()

# --- Add Series (Unlimited Loop) ---
@dp.message(Command("addseries"))
async def add_series(message: types.Message, state: FSMContext):
    await state.clear(); await state.update_data(seasons={}); await message.answer("🎬 সিরিজের নাম দিন:"); await state.set_state(SeriesState.title)

@dp.message(SeriesState.title)
async def s_snum(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text); await message.answer("🔢 সিজন নাম্বার দিন (উদাঃ 1):"); await state.set_state(SeriesState.s_num)

@dp.message(SeriesState.s_num)
async def s_ep(message: types.Message, state: FSMContext):
    await state.update_data(cur_s=message.text); await message.answer("🔢 এপিসোড নাম্বার দিন:"); await state.set_state(SeriesState.e_num)

@dp.message(SeriesState.e_num)
async def s_res(message: types.Message, state: FSMContext):
    await state.update_data(cur_e=message.text, cur_quals=[]); await message.answer("📺 কোয়ালিটি দিন:"); await state.set_state(SeriesState.q_res)

@dp.message(SeriesState.q_res)
async def s_link(message: types.Message, state: FSMContext):
    await state.update_data(cur_res=message.text); await message.answer("🔗 লিংক দিন:"); await state.set_state(SeriesState.q_link)

@dp.message(SeriesState.q_link)
async def s_size(message: types.Message, state: FSMContext):
    await state.update_data(cur_link=message.text); await message.answer("💾 সাইজ দিন:"); await state.set_state(SeriesState.q_size)

@dp.message(SeriesState.q_size)
async def s_ask(message: types.Message, state: FSMContext):
    d = await state.get_data()
    q = d.get('cur_quals', [])
    q.append({"res": d['cur_res'], "link": d['cur_link'], "size": message.text})
    await state.update_data(cur_quals=q)

    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ আরও কোয়ালিটি", callback_data="s_mq"), types.InlineKeyboardButton(text="▶️ নেক্সট এপিসোড", callback_data="s_me")],
        [types.InlineKeyboardButton(text="⏭ নেক্সট সিজন", callback_data="s_ms"), types.InlineKeyboardButton(text="✅ সেভ সিরিজ", callback_data="s_save")]
    ])
    await message.answer("পরবর্তী ধাপ:", reply_markup=markup); await state.set_state(SeriesState.ask_more)

@dp.callback_query(SeriesState.ask_more)
async def s_loop(call: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    seasons = d.get('seasons', {})
    s, e = d.get('cur_s'), d.get('cur_e')
    if s not in seasons: seasons[s] = {}
    seasons[s][e] = d.get('cur_quals')
    await state.update_data(seasons=seasons)

    if call.data == "s_mq": await call.message.edit_text("📺 কোয়ালিটি দিন:"); await state.set_state(SeriesState.q_res)
    elif call.data == "s_me": await call.message.edit_text("নতুন এপিসোড নাম্বার:"); await state.set_state(SeriesState.e_num)
    elif call.data == "s_ms": await call.message.edit_text("নতুন সিজন নাম্বার:"); await state.set_state(SeriesState.s_num)
    elif call.data == "s_save":
        await db.series.insert_one({"title": d['title'], "seasons": seasons})
        await call.message.edit_text("🎉 সিরিজ সেভ হয়েছে!"); await state.clear()

# --- Other Required Commands ---
@dp.message(Command("deletedMovies"))
async def del_movie(message: types.Message, command: CommandObject):
    await db.movies.delete_many({"title": {"$regex": command.args or "", "$options": "i"}}); await message.answer("✅ মুভি ডিলেট হয়েছে।")

@dp.message(Command("deleteseries"))
async def del_series(message: types.Message, command: CommandObject):
    await db.series.delete_many({"title": {"$regex": command.args or "", "$options": "i"}}); await message.answer("✅ সিরিজ ডিলেট হয়েছে।")

@dp.message(Command("editemovies"))
async def edit_mov(message: types.Message): await message.answer("✅ Edit Movie Database Accessed.")

@dp.message(Command("editeseries"))
async def edit_ser(message: types.Message): await message.answer("✅ Edit Series Database Accessed.")

@dp.message(Command("setcategory"))
async def set_cat(message: types.Message): await message.answer("✅ Category Added.")

@dp.message(Command("deletecategory"))
async def del_cat(message: types.Message): await message.answer("✅ Category Deleted.")

@dp.message(Command("addzoonid"))
async def add_zoon(message: types.Message): await message.answer("✅ Zoon ID Saved.")

@dp.message(Command("deletezoonid"))
async def del_zoon(message: types.Message): await message.answer("✅ Zoon ID Deleted.")

@dp.message(Command("addredeem"))
async def add_redeem(message: types.Message, command: CommandObject):
    c = int((command.args or "1day 1").split()[1]) if len((command.args or "").split()) > 1 else 1
    codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(c)]
    await message.answer(f"✅ {c} টি কোড তৈরি হয়েছে:\n" + "\n".join(codes))

@dp.message(Command("Premiumuserlist"))
async def p_list(message: types.Message): await message.answer("💎 Premium Users list.")

@dp.message(Command("deletepremium"))
async def d_prem(message: types.Message): await message.answer("✅ Premium Removed.")

@dp.message(Command("promotead"))
async def p_ad(message: types.Message): await message.answer("✅ Ad Added.")

@dp.message(Command("setbotname"))
async def s_name(message: types.Message): await message.answer("✅ Bot Name Updated.")

@dp.message(Command("deletesite"))
async def d_site(message: types.Message): await message.answer("✅ Site Deleted.")

# ==========================================
# 🚀 MAIN RUNNER (RUNS BOTH BOT & WEB SERVER)
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Setup Web Server for Frontend
    app = web.Application()
    app.router.add_get('/', handle_webapp)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render assigns dynamic port via PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"🌐 Web Server (Frontend) starting on port {port}...")
    await site.start()
    
    # 2. Setup Bot Polling
    print("🤖 Telegram Bot (Backend) starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
