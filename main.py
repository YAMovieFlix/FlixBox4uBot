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
# ⚙️ ১. কনফিগারেশন (আপনার ডাটা দিন)
# ==========================================
BOT_TOKEN = "9219855483:AAH9ZrxFejeC_j9X697I_UOGSlnneH1_bSs"
MONGO_URI = "YOUR_MONGODB_URI_HERE"
WEB_APP_URL = "https://flixbox4ubot.onrender.com"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client['MovieeLinkDB']

# ==========================================
# 🌐 ২. ফ্রন্টএন্ড ওয়েব অ্যাপ (Real Dynamic UI)
# ==========================================
HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>MovieeLink App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <!-- Monetag Ad Script -->
    <script src="https://alwingulla.com/88/tag.min.js" data-zone="YOUR_ZONE_ID"></script>
</head>
<body class="bg-[#f4f4f5] text-gray-800 font-sans pb-20">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- 🏠 Home Page (Real Dynamic Data) ---
        const HomePage = ({ data, onSelect }) => (
            <div className="bg-white min-h-screen relative pb-6">
                <div className="flex items-center gap-3 p-4 border-b border-gray-100">
                    <h1 className="text-xl font-bold text-gray-800 flex-1">Moviee <span className="bg-red-500 text-white px-2 py-0.5 rounded text-sm">Link</span></h1>
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-xl text-gray-500 shadow-inner">🔍</div>
                </div>

                {/* Sliders */}
                <div className="flex overflow-x-auto gap-4 p-4 snap-x hide-scrollbar mt-2">
                    {data.sliders.length > 0 ? data.sliders.map((img, i) => (
                        <img key={i} src={img} className="w-[85vw] h-48 object-cover rounded-2xl snap-center shrink-0 shadow-md" alt="Slider" />
                    )) : (
                        <div className="w-[85vw] h-48 bg-gray-200 rounded-2xl flex items-center justify-center snap-center shrink-0">No Sliders Added</div>
                    )}
                </div>

                <div className="p-4 space-y-5">
                    {data.items.length === 0 && <p className="text-center text-gray-400 mt-10">কোনো মুভি বা সিরিজ আপলোড করা হয়নি!</p>}
                    {/* Database থেকে আসা আসল মুভি ও সিরিজ ম্যাপ করা হচ্ছে */}
                    {data.items.map((item, i) => (
                        <div key={i} onClick={() => onSelect(item)} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden relative cursor-pointer active:scale-95 transition-transform">
                            <img src={item.thumb} className="w-full h-48 object-cover" />
                            <div className="p-3">
                                <h3 className="font-bold text-lg text-gray-800">{item.title}</h3>
                                <p className="text-xs text-gray-500 mt-1">
                                    <span className={item.type === 'movie' ? 'text-blue-500 font-bold' : 'text-purple-500 font-bold'}>
                                        {item.type === 'movie' ? 'MOVIE' : 'WEB SERIES'}
                                    </span> 
                                    • {item.year} • {item.language} • {item.category}
                                </p>
                            </div>
                            <button className="absolute bottom-3 right-3 bg-red-500 text-white px-5 py-1.5 rounded-full text-xs font-bold shadow-md">Open</button>
                        </div>
                    ))}
                </div>
            </div>
        );

        // --- 🎬 Details Page (15s Ad & Real Download Links) ---
        const DetailsPage = ({ item, goBack }) => {
            const [adTimer, setAdTimer] = useState(0);
            const [isAdRunning, setIsAdRunning] = useState(false);
            const [isUnlocked, setIsUnlocked] = useState(false);

            const handleUnlock = () => {
                if(window.showMonetagAd) window.showMonetagAd(); 
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
                <div className="bg-white min-h-screen">
                    <div className="relative">
                        <button onClick={goBack} className="absolute top-3 left-3 bg-black/50 text-white w-8 h-8 rounded-full flex items-center justify-center z-10">✕</button>
                        <img src={item.thumb} className="w-full h-64 object-cover" />
                        <span className="absolute top-3 right-3 bg-yellow-400 text-black px-2 py-0.5 text-xs font-bold rounded shadow">HD</span>
                    </div>
                    <div className="p-4">
                        <h1 className="text-xl font-bold text-gray-900">{item.title}</h1>
                        <p className="text-sm text-gray-500 mb-4">{item.year} | {item.language} | {item.category}</p>

                        {!isUnlocked ? (
                            <button onClick={handleUnlock} disabled={isAdRunning} className={`w-full py-3.5 rounded-xl font-bold mb-3 transition-all shadow-sm ${isAdRunning ? 'bg-[#fff1ec] text-[#e65c2a]' : 'bg-red-500 text-white'}`}>
                                {isAdRunning ? `⏳ Please wait... ${adTimer}s (Ad is showing)` : '💡 Tap Here to Unlock Download Links'}
                            </button>
                        ) : (
                            <div className="bg-green-50 border border-green-200 p-4 rounded-xl mb-4">
                                <h3 className="font-bold text-green-700 mb-3">✅ Download Links Ready:</h3>
                                
                                {/* মুভির ডাউনলোড লিংক গুলা */}
                                {item.type === 'movie' && item.qualities && item.qualities.map((q, i) => (
                                    <a key={i} href={q.link} target="_blank" className="block w-full text-center bg-green-500 text-white py-2 rounded-lg mb-2 font-bold shadow-sm">
                                        ⬇ Download {q.res} ({q.size})
                                    </a>
                                ))}

                                {/* সিরিজের সিজন ও এপিসোড এর ডাউনলোড লিংক গুলা */}
                                {item.type === 'series' && item.seasons && Object.keys(item.seasons).map(seasonNum => (
                                    <div key={seasonNum} className="mb-4">
                                        <h4 className="font-bold text-indigo-700 bg-indigo-100 p-2 rounded">Season {seasonNum}</h4>
                                        {Object.keys(item.seasons[seasonNum]).map(epNum => (
                                            <div key={epNum} className="ml-2 mt-2 border-l-2 border-indigo-200 pl-2">
                                                <p className="font-semibold text-sm text-gray-700 mb-1">Episode {epNum}</p>
                                                {item.seasons[seasonNum][epNum].map((q, i) => (
                                                    <a key={i} href={q.link} target="_blank" className="inline-block bg-blue-500 text-white text-xs px-3 py-1.5 rounded mr-2 mb-1">
                                                        ⬇ {q.res} ({q.size})
                                                    </a>
                                                ))}
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            );
        };

        // --- 📱 Main App Component ---
        const App = () => {
            const [view, setView] = useState('home'); // home, details
            const [appData, setAppData] = useState({ items: [], sliders: [] });
            const [selectedItem, setSelectedItem] = useState(null);

            useEffect(() => {
                if(window.Telegram?.WebApp) window.Telegram.WebApp.expand();
                // ব্যাকএন্ড থেকে আসল ডাটা আনা হচ্ছে
                fetch('/api/data').then(r => r.json()).then(data => setAppData(data));
            }, []);

            return (
                <div className="relative">
                    {view === 'home' && <HomePage data={appData} onSelect={(item) => { setSelectedItem(item); setView('details'); }} />}
                    {view === 'details' && selectedItem && <DetailsPage item={selectedItem} goBack={() => setView('home')} />}
                    
                    {/* Bottom Navigation */}
                    <div className="fixed bottom-0 w-full bg-[#f4f4f5] border-t border-gray-200 flex justify-around px-2 py-2.5 text-[10px] text-gray-500 font-medium z-40">
                        <button onClick={() => setView('home')} className={`flex flex-col items-center ${view==='home'?'text-red-500':''}`}><span className="text-[22px] mb-0.5">🏠</span> Home</button>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
    <style>
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</body>
</html>
"""

# ==========================================
# 🌐 ৩. ওয়েব সার্ভার এপিআই (আসল ডাটা পাঠানো)
# ==========================================
async def handle_webapp(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_api_data(request):
    # ডাটাবেস থেকে মুভি ও সিরিজ নিয়ে আসা হচ্ছে
    movies = await db.movies.find({"type": "movie"}).sort('_id', -1).to_list(50)
    series = await db.series.find({"type": "series"}).sort('_id', -1).to_list(50)
    
    # সব আইটেম এক সাথে মিক্স করে পাঠানো হচ্ছে ফ্রন্টএন্ডে
    all_items = movies + series
    for item in all_items: 
        item['_id'] = str(item['_id']) # JSON error fix
    
    sliders_doc = await db.settings.find_one({"type": "sliders"})
    sliders = sliders_doc['list'] if sliders_doc else []
    
    return web.json_response({"items": all_items, "sliders": sliders})

# ==========================================
# 🤖 ৪. বট লজিক (FSM এবং Error Handling)
# ==========================================
class MovieState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    thumb = State() # <-- এই স্টেপটি নতুন এড করা হয়েছে ছবির জন্য
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class SeriesState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    thumb = State() # <-- সিরিজের ছবির জন্য
    s_num = State(); e_num = State()
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

# --- 🎯 /start ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🍿 WATCH NOW", web_app=types.WebAppInfo(url=WEB_APP_URL))],
    ])
    await message.answer("👋 **Welcome to MovieeLink Bot!**\n\n🎬 নিচের বাটনে ক্লিক করে ওয়েবসাইট ওপেন করুন।", reply_markup=markup, parse_mode="Markdown")

# --- ❌ Cancel Command (ফ্লো থেকে বের হতে) ---
@dp.message(Command("cancel"))
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ আপনি বর্তমান প্রক্রিয়াটি বাতিল করেছেন।")

# --- 🎬 মুভি আপলোড লজিক (আসল FSM) ---
@dp.message(Command("movies"))
async def add_movie(message: types.Message, state: FSMContext):
    await state.clear(); await message.answer("🎬 মুভির নাম দিন:"); await state.set_state(MovieState.title)

@dp.message(MovieState.title)
async def m_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text, qualities=[]); await message.answer("📅 সাল দিন (উদাঃ 2024):"); await state.set_state(MovieState.year)

@dp.message(MovieState.year)
async def m_cat(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text); await message.answer("📁 ক্যাটাগরি লিখুন:"); await state.set_state(MovieState.category)

@dp.message(MovieState.category)
async def m_lang(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text); await message.answer("🗣 ভাষা লিখুন:"); await state.set_state(MovieState.language)

@dp.message(MovieState.language)
async def m_thumb(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    # এখানে বট আপনার কাছে ছবি চাইবে
    await message.answer("🖼 এবার মুভির পোস্টার বা ছবি দিন (Telegram এ Photo হিসেবে আপলোড দিন অথবা ছবির ডিরেক্ট লিংক দিন):")
    await state.set_state(MovieState.thumb)

@dp.message(MovieState.thumb)
async def m_res(message: types.Message, state: FSMContext):
    # যদি ছবি আপলোড করে তাহলে তার ফাইল পাথ থেকে লিংক জেনারেট হবে
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        thumb_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    else:
        thumb_url = message.text # যদি ডিরেক্ট লিংক দেয়
        
    await state.update_data(thumb=thumb_url)
    await message.answer("📺 কোয়ালিটি দিন (উদাঃ 720p, 1080p):")
    await state.set_state(MovieState.q_res)

@dp.message(MovieState.q_res)
async def m_link(message: types.Message, state: FSMContext):
    await state.update_data(cur_res=message.text); await message.answer("🔗 ডাউনলোড লিংক দিন:"); await state.set_state(MovieState.q_link)

@dp.message(MovieState.q_link)
async def m_size(message: types.Message, state: FSMContext):
    await state.update_data(cur_link=message.text); await message.answer("💾 সাইজ দিন (উদাঃ 1.2GB):"); await state.set_state(MovieState.q_size)

@dp.message(MovieState.q_size)
async def m_ask(message: types.Message, state: FSMContext):
    d = await state.get_data()
    quals = d.get('qualities', [])
    quals.append({"res": d['cur_res'], "link": d['cur_link'], "size": message.text})
    await state.update_data(qualities=quals)
    
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ আরও কোয়ালিটি এড করুন", callback_data="m_more")],
        [types.InlineKeyboardButton(text="✅ সম্পূর্ণ মুভি সেভ করুন", callback_data="m_save")]
    ])
    await message.answer(f"✅ {len(quals)} টি কোয়ালিটি এড হয়েছে। পরবর্তী ধাপ:", reply_markup=markup)
    await state.set_state(MovieState.ask_more)

@dp.callback_query(MovieState.ask_more)
async def m_save(call: types.CallbackQuery, state: FSMContext):
    if call.data == "m_more":
        await call.message.edit_text("📺 নতুন কোয়ালিটি দিন (উদাঃ 480p):"); await state.set_state(MovieState.q_res)
    else:
        d = await state.get_data()
        # মংগোডিবিতে সেভ
        await db.movies.insert_one({
            "type": "movie", "title": d['title'], "year": d['year'], 
            "category": d['category'], "language": d['language'], 
            "thumb": d['thumb'], "qualities": d['qualities']
        })
        await call.message.edit_text(f"🎉 **{d['title']}** সফলভাবে আপলোড হয়েছে! মিনি অ্যাপ ওপেন করে চেক করুন।", parse_mode="Markdown")
        await state.clear()

# --- 🎥 সিরিজ আপলোড লজিক ---
@dp.message(Command("addseries"))
async def add_series(message: types.Message, state: FSMContext):
    await state.clear(); await state.update_data(seasons={}); await message.answer("🎬 সিরিজের নাম দিন:"); await state.set_state(SeriesState.title)

@dp.message(SeriesState.title)
async def s_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text); await message.answer("📅 সাল দিন (উদাঃ 2026):"); await state.set_state(SeriesState.year)

@dp.message(SeriesState.year)
async def s_cat(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text); await message.answer("📁 ক্যাটাগরি দিন:"); await state.set_state(SeriesState.category)

@dp.message(SeriesState.category)
async def s_lang(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text); await message.answer("🗣 ভাষা দিন:"); await state.set_state(SeriesState.language)

@dp.message(SeriesState.language)
async def s_thumb(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer("🖼 সিরিজের পোস্টার বা ছবি দিন (ছবি আপলোড করুন অথবা লিংক দিন):")
    await state.set_state(SeriesState.thumb)

@dp.message(SeriesState.thumb)
async def s_snum(message: types.Message, state: FSMContext):
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        thumb_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    else:
        thumb_url = message.text
    await state.update_data(thumb=thumb_url)
    await message.answer("🔢 প্রথম সিজন নাম্বার দিন (উদাঃ 1):")
    await state.set_state(SeriesState.s_num)

@dp.message(SeriesState.s_num)
async def s_ep(message: types.Message, state: FSMContext):
    await state.update_data(cur_s=message.text); await message.answer(f"সিজন {message.text} এর 🔢 প্রথম এপিসোড নাম্বার দিন (উদাঃ 1):"); await state.set_state(SeriesState.e_num)

@dp.message(SeriesState.e_num)
async def s_res(message: types.Message, state: FSMContext):
    await state.update_data(cur_e=message.text, cur_quals=[]); await message.answer("📺 কোয়ালিটি দিন (উদাঃ 720p):"); await state.set_state(SeriesState.q_res)

@dp.message(SeriesState.q_res)
async def s_link(message: types.Message, state: FSMContext):
    await state.update_data(cur_res=message.text); await message.answer("🔗 ডাউনলোড লিংক দিন:"); await state.set_state(SeriesState.q_link)

@dp.message(SeriesState.q_link)
async def s_size(message: types.Message, state: FSMContext):
    await state.update_data(cur_link=message.text); await message.answer("💾 সাইজ দিন (উদাঃ 400MB):"); await state.set_state(SeriesState.q_size)

@dp.message(SeriesState.q_size)
async def s_ask(message: types.Message, state: FSMContext):
    d = await state.get_data()
    q = d.get('cur_quals', [])
    q.append({"res": d['cur_res'], "link": d['cur_link'], "size": message.text})
    await state.update_data(cur_quals=q)

    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="➕ এই এপিসোডে আরও কোয়ালিটি", callback_data="s_mq")],
        [types.InlineKeyboardButton(text="▶️ নতুন এপিসোড এড করুন", callback_data="s_me")],
        [types.InlineKeyboardButton(text="⏭ নতুন সিজন এড করুন", callback_data="s_ms")],
        [types.InlineKeyboardButton(text="✅ সম্পূর্ণ সিরিজ সেভ করুন", callback_data="s_save")]
    ])
    await message.answer("পরবর্তী ধাপ সিলেক্ট করুন:", reply_markup=markup)
    await state.set_state(SeriesState.ask_more)

@dp.callback_query(SeriesState.ask_more)
async def s_loop(call: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    seasons = d.get('seasons', {})
    s, e = d.get('cur_s'), d.get('cur_e')
    if s not in seasons: seasons[s] = {}
    seasons[s][e] = d.get('cur_quals')
    await state.update_data(seasons=seasons)

    if call.data == "s_mq": await call.message.edit_text("📺 নতুন কোয়ালিটি দিন:"); await state.set_state(SeriesState.q_res)
    elif call.data == "s_me": await call.message.edit_text(f"সিজন {s} এর নতুন এপিসোড নাম্বার দিন:"); await state.set_state(SeriesState.e_num)
    elif call.data == "s_ms": await call.message.edit_text("নতুন সিজন নাম্বার দিন:"); await state.set_state(SeriesState.s_num)
    elif call.data == "s_save":
        await db.series.insert_one({
            "type": "series", "title": d['title'], "year": d['year'], 
            "category": d['category'], "language": d['language'], 
            "thumb": d['thumb'], "seasons": seasons
        })
        await call.message.edit_text(f"🎉 **{d['title']}** সম্পূর্ণ সিরিজ আপলোড হয়েছে!", parse_mode="Markdown"); await state.clear()

# --- 🛠 অন্যান্য কমান্ড ---
@dp.message(Command("addslider"))
async def add_slider(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/addslider https://image.link/img.jpg`", parse_mode="Markdown")
    await db.settings.update_one({"type": "sliders"}, {"$addToSet": {"list": command.args}}, upsert=True)
    await message.answer("✅ Slider Image Added!")

@dp.message(Command("deletedMovies"))
async def del_movie(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/deletedMovies RRR`", parse_mode="Markdown")
    res = await db.movies.delete_many({"title": {"$regex": command.args, "$options": "i"}})
    await message.answer(f"✅ {res.deleted_count} টি মুভি ডিলেট হয়েছে।")

@dp.message(Command("deleteseries"))
async def del_series(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/deleteseries Batchlor Point`", parse_mode="Markdown")
    res = await db.series.delete_many({"title": {"$regex": command.args, "$options": "i"}})
    await message.answer(f"✅ {res.deleted_count} টি সিরিজ ডিলেট হয়েছে।")

# ==========================================
# 🚀 ৫. Main Runner (বট ও ওয়েবসাইট একসাথে)
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # ❗️ এই লাইনটি আটকে থাকা মেসেজ রিমুভ করে বটকে সচল করবে (Command not working issue fix) ❗️
    await bot.delete_webhook(drop_pending_updates=True)
    
    app = web.Application()
    app.router.add_get('/', handle_webapp)
    app.router.add_get('/api/data', handle_api_data) 
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"🌐 Web Server running on port {port}...")
    await site.start()
    
    print("🤖 Telegram Bot starting... All commands will work now!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
