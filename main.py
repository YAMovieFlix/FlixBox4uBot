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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient

# ==========================================
# ⚙️ ১. কনফিগারেশন (আপনার ডাটা দিন)
# ==========================================
BOT_TOKEN = "9219855483:AAH9ZrxFejeC_j9X697I_UOGSlnneH1_bSs"
MONGO_URI = "YOUR_MONGODB_URI_HERE"
WEB_APP_URL = "https://flixbox4ubot.onrender.com"

# ❗️ এখানে আপনার টেলিগ্রাম User ID দিন, যাতে শুধু আপনি এডমিন হিসেবে কমান্ড দিতে পারেন ❗️
ADMIN_ID = 7120801813 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client['MovieeLinkDB']

# এডমিন চেক করার ফাংশন
def is_admin(user_id):
    return user_id == ADMIN_ID

# ==========================================
# 🌐 ২. ফ্রন্টএন্ড ওয়েব অ্যাপ (React + Tailwind)
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
</head>
<body class="bg-[#f4f4f5] text-gray-800 font-sans pb-20">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        const HomePage = ({ data, onSelect }) => (
            <div className="bg-white min-h-screen relative pb-6">
                <div className="flex items-center gap-3 p-4 border-b border-gray-100 shadow-sm">
                    <h1 className="text-xl font-bold text-gray-800 flex-1">{data.botname || "Moviee"} <span className="bg-red-500 text-white px-2 py-0.5 rounded text-sm">Link</span></h1>
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-xl text-gray-500 shadow-inner">🔍</div>
                </div>

                {data.promo && (
                    <div className="bg-indigo-600 text-white text-xs py-2 px-4 flex items-center gap-2">
                        <span className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></span>
                        <marquee className="flex-1 text-[12px] font-medium">{data.promo}</marquee>
                    </div>
                )}

                <div className="flex overflow-x-auto gap-4 p-4 snap-x hide-scrollbar mt-2">
                    {data.sliders.length > 0 ? data.sliders.map((img, i) => (
                        <img key={i} src={img} className="w-[85vw] h-48 object-cover rounded-2xl snap-center shrink-0 shadow-md" alt="Slider" />
                    )) : (
                        <div className="w-[85vw] h-48 bg-gray-200 rounded-2xl flex items-center justify-center snap-center shrink-0">No Sliders</div>
                    )}
                </div>

                <div className="p-4 space-y-5">
                    {data.items.length === 0 && <p className="text-center text-gray-400 mt-10">কোনো মুভি বা সিরিজ আপলোড করা হয়নি!</p>}
                    {data.items.map((item, i) => (
                        <div key={i} onClick={() => onSelect(item)} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden relative cursor-pointer active:scale-95 transition-transform">
                            <img src={item.thumb} className="w-full h-48 object-cover" />
                            <div className="p-3">
                                <h3 className="font-bold text-lg text-gray-800">{item.title}</h3>
                                <p className="text-xs text-gray-500 mt-1">
                                    <span className={item.type === 'movie' ? 'text-blue-500 font-bold' : 'text-purple-500 font-bold'}>
                                        {item.type === 'movie' ? 'MOVIE' : 'SERIES'}
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

        const DetailsPage = ({ item, goBack, zoonid }) => {
            const [adTimer, setAdTimer] = useState(0);
            const [isAdRunning, setIsAdRunning] = useState(false);
            const [isUnlocked, setIsUnlocked] = useState(false);

            useEffect(() => {
                // ডাইনামিক Monetag Script এড করা
                if(zoonid && !document.getElementById('monetag-script')) {
                    const script = document.createElement('script');
                    script.src = "https://alwingulla.com/88/tag.min.js";
                    script.setAttribute('data-zone', zoonid);
                    script.id = 'monetag-script';
                    document.body.appendChild(script);
                }
            }, [zoonid]);

            const handleUnlock = () => {
                if(isUnlocked) return;
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
                            <button onClick={handleUnlock} disabled={isAdRunning} className={`w-full py-3.5 rounded-xl font-bold mb-4 transition-all shadow-sm ${isAdRunning ? 'bg-[#fff1ec] text-[#e65c2a]' : 'bg-red-500 text-white'}`}>
                                {isAdRunning ? `⏳ Please wait... ${adTimer}s (Ad is showing)` : '💡 Tap Here to Unlock Download Links'}
                            </button>
                        ) : (
                            <div className="bg-green-50 border border-green-200 p-4 rounded-xl mb-4">
                                <h3 className="font-bold text-green-700 mb-3">✅ Download Links Ready:</h3>
                                {item.type === 'movie' && item.qualities && item.qualities.map((q, i) => (
                                    <a key={i} href={q.link} target="_blank" className="block w-full text-center bg-green-500 text-white py-2 rounded-lg mb-2 font-bold shadow-sm">
                                        ⬇ Download {q.res} ({q.size})
                                    </a>
                                ))}
                                {item.type === 'series' && item.seasons && Object.keys(item.seasons).map(sNum => (
                                    <div key={sNum} className="mb-4">
                                        <h4 className="font-bold text-indigo-700 bg-indigo-100 p-2 rounded">Season {sNum}</h4>
                                        {Object.keys(item.seasons[sNum]).map(epNum => (
                                            <div key={epNum} className="ml-2 mt-2 border-l-2 border-indigo-200 pl-2">
                                                <p className="font-semibold text-sm text-gray-700 mb-1">Episode {epNum}</p>
                                                {item.seasons[sNum][epNum].map((q, i) => (
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

        const App = () => {
            const [view, setView] = useState('home');
            const [appData, setAppData] = useState({ items: [], sliders: [], zoonid: '', botname: '', promo: '' });
            const [selectedItem, setSelectedItem] = useState(null);

            useEffect(() => {
                if(window.Telegram?.WebApp) window.Telegram.WebApp.expand();
                fetch('/api/data').then(r => r.json()).then(data => setAppData(data));
            }, []);

            return (
                <div className="relative">
                    {view === 'home' && <HomePage data={appData} onSelect={(item) => { setSelectedItem(item); setView('details'); }} />}
                    {view === 'details' && selectedItem && <DetailsPage item={selectedItem} goBack={() => setView('home')} zoonid={appData.zoonid} />}
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
# 🌐 ৩. ওয়েব সার্ভার এপিআই
# ==========================================
async def handle_webapp(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_api_data(request):
    movies = await db.movies.find({"type": "movie"}).sort('_id', -1).to_list(50)
    series = await db.series.find({"type": "series"}).sort('_id', -1).to_list(50)
    all_items = movies + series
    for item in all_items: item['_id'] = str(item['_id'])
    
    settings = await db.settings.find().to_list(100)
    data = {"items": all_items, "sliders": [], "zoonid": "", "botname": "Moviee", "promo": ""}
    for s in settings:
        if s['type'] == 'sliders': data['sliders'] = s.get('list', [])
        elif s['type'] == 'zoonid': data['zoonid'] = s.get('id', '')
        elif s['type'] == 'botname': data['botname'] = s.get('name', 'Moviee')
        elif s['type'] == 'promo': data['promo'] = s.get('text', '')
    
    return web.json_response(data)

# ==========================================
# 🤖 ৪. FSM স্টেটস
# ==========================================
class MovieState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    thumb = State(); q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class SeriesState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    thumb = State(); s_num = State(); e_num = State()
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class EditMovieState(StatesGroup):
    select_action = State(); res = State(); link = State(); size = State()

class EditSeriesState(StatesGroup):
    select_action = State(); s_num = State(); e_num = State()
    res = State(); link = State(); size = State(); ask_more = State()

# ==========================================
# 🚀 ৫. টেলিগ্রাম কমান্ডস ও লজিক (Only Admin)
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍿 WATCH NOW", web_app=types.WebAppInfo(url=WEB_APP_URL))],
    ])
    await message.answer("👋 **Welcome to MovieeLink Bot!**\n\n🎬 নিচের বাটনে ক্লিক করে ওয়েবসাইট ওপেন করুন।", reply_markup=markup, parse_mode="Markdown")

# --- 🎬 ADD MOVIE FLOW ---
@dp.message(Command("movies"))
async def add_movie_cmd(message: types.Message, command: CommandObject, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.clear()
    
    # /movies RRR 2024 (নাম ও সাল এক সাথে নিলে)
    if command.args:
        args = command.args.rsplit(' ', 1)
        title = args[0]
        year = args[1] if len(args)>1 else "2024"
        await state.update_data(title=title, year=year, qualities=[])
        await prompt_category(message, state)
    else:
        await message.answer("🎬 মুভির নাম দিন (উদাঃ RRR):")
        await state.set_state(MovieState.title)

@dp.message(MovieState.title)
async def m_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text, qualities=[])
    await message.answer("📅 সাল দিন (উদাঃ 2024):")
    await state.set_state(MovieState.year)

@dp.message(MovieState.year)
async def m_cat_prompt(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await prompt_category(message, state)

async def prompt_category(message, state):
    cat_doc = await db.settings.find_one({"type": "categories"})
    cats = cat_doc['list'] if cat_doc else ["Action", "Romance", "Comedy"]
    kb = [[InlineKeyboardButton(text=c, callback_data=f"mcat_{c}")] for c in cats]
    await message.answer("📁 ক্যাটাগরি সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(MovieState.category)

@dp.callback_query(MovieState.category)
async def m_lang_prompt(call: types.CallbackQuery, state: FSMContext):
    cat = call.data.split('_')[1]
    await state.update_data(category=cat)
    langs = ["Bangla", "Hindi", "English", "Tamil"]
    kb = [[InlineKeyboardButton(text=l, callback_data=f"mlang_{l}")] for l in langs]
    await call.message.edit_text("🗣 ভাষা সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(MovieState.language)

@dp.callback_query(MovieState.language)
async def m_thumb(call: types.CallbackQuery, state: FSMContext):
    lang = call.data.split('_')[1]
    await state.update_data(language=lang)
    await call.message.edit_text("🖼 এবার মুভির পোস্টার বা ছবি দিন (Upload photo or send link):")
    await state.set_state(MovieState.thumb)

@dp.message(MovieState.thumb)
async def m_res(message: types.Message, state: FSMContext):
    thumb_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{(await bot.get_file(message.photo[-1].file_id)).file_path}" if message.photo else message.text
    await state.update_data(thumb=thumb_url)
    await message.answer("📺 কোয়ালিটি দিন (উদাঃ 720p, 1080p):")
    await state.set_state(MovieState.q_res)

@dp.message(MovieState.q_res)
async def m_link(message: types.Message, state: FSMContext):
    await state.update_data(cur_res=message.text); await message.answer("🔗 ডাউনলোড লিংক দিন:")
    await state.set_state(MovieState.q_link)

@dp.message(MovieState.q_link)
async def m_size(message: types.Message, state: FSMContext):
    await state.update_data(cur_link=message.text); await message.answer("💾 সাইজ দিন (উদাঃ 1.2GB):")
    await state.set_state(MovieState.q_size)

@dp.message(MovieState.q_size)
async def m_ask(message: types.Message, state: FSMContext):
    d = await state.get_data()
    q = d.get('qualities', [])
    q.append({"res": d['cur_res'], "link": d['cur_link'], "size": message.text})
    await state.update_data(qualities=q)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ আরও কোয়ালিটি এড", callback_data="m_more")],
        [InlineKeyboardButton(text="✅ সেভ করুন (Skip)", callback_data="m_save")]
    ])
    await message.answer(f"✅ {len(q)} টি কোয়ালিটি এড হয়েছে। পরবর্তী ধাপ:", reply_markup=markup)
    await state.set_state(MovieState.ask_more)

@dp.callback_query(MovieState.ask_more)
async def m_save(call: types.CallbackQuery, state: FSMContext):
    if call.data == "m_more":
        await call.message.edit_text("📺 নতুন কোয়ালিটি দিন:"); await state.set_state(MovieState.q_res)
    else:
        d = await state.get_data()
        await db.movies.insert_one({"type": "movie", "title": d['title'], "year": d['year'], "category": d['category'], "language": d['language'], "thumb": d['thumb'], "qualities": d['qualities']})
        await call.message.edit_text(f"🎉 **{d['title']}** সফলভাবে আপলোড হয়েছে!", parse_mode="Markdown")
        await state.clear()

# --- 🎥 ADD SERIES FLOW ---
@dp.message(Command("addseries"))
async def add_series_cmd(message: types.Message, command: CommandObject, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.clear(); await state.update_data(seasons={})
    
    if command.args:
        args = command.args.rsplit(' ', 1)
        title = args[0]
        year = args[1] if len(args)>1 else "2024"
        await state.update_data(title=title, year=year)
        await prompt_series_category(message, state)
    else:
        await message.answer("🎬 সিরিজের নাম দিন:"); await state.set_state(SeriesState.title)

@dp.message(SeriesState.title)
async def s_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text); await message.answer("📅 সাল দিন (উদাঃ 2026):"); await state.set_state(SeriesState.year)

@dp.message(SeriesState.year)
async def s_cat_prompt(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text); await prompt_series_category(message, state)

async def prompt_series_category(message, state):
    cat_doc = await db.settings.find_one({"type": "categories"})
    cats = cat_doc['list'] if cat_doc else ["Action", "Romance", "Comedy"]
    kb = [[InlineKeyboardButton(text=c, callback_data=f"scat_{c}")] for c in cats]
    await message.answer("📁 ক্যাটাগরি সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(SeriesState.category)

@dp.callback_query(SeriesState.category)
async def s_lang_prompt(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data.split('_')[1])
    langs = ["Bangla", "Hindi", "English"]
    kb = [[InlineKeyboardButton(text=l, callback_data=f"slang_{l}")] for l in langs]
    await call.message.edit_text("🗣 ভাষা সিলেক্ট করুন:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(SeriesState.language)

@dp.callback_query(SeriesState.language)
async def s_thumb(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(language=call.data.split('_')[1])
    await call.message.edit_text("🖼 সিরিজের ছবি দিন (Upload photo/link):"); await state.set_state(SeriesState.thumb)

@dp.message(SeriesState.thumb)
async def s_snum(message: types.Message, state: FSMContext):
    thumb_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{(await bot.get_file(message.photo[-1].file_id)).file_path}" if message.photo else message.text
    await state.update_data(thumb=thumb_url)
    await message.answer("🔢 প্রথম সিজন নাম্বার দিন (উদাঃ 1):"); await state.set_state(SeriesState.s_num)

@dp.message(SeriesState.s_num)
async def s_ep(message: types.Message, state: FSMContext):
    await state.update_data(cur_s=message.text); await message.answer(f"সিজন {message.text} এর 🔢 প্রথম এপিসোড নাম্বার দিন:"); await state.set_state(SeriesState.e_num)

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

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ আরও কোয়ালিটি", callback_data="s_mq")],
        [InlineKeyboardButton(text="▶️ নতুন এপিসোড", callback_data="s_me"), InlineKeyboardButton(text="⏭ নতুন সিজন", callback_data="s_ms")],
        [InlineKeyboardButton(text="✅ সেভ করুন", callback_data="s_save")]
    ])
    await message.answer(f"✅ সিজন {d['cur_s']} | এপিসোড {d['cur_e']} | কোয়ালিটি {len(q)} টি এড হয়েছে।", reply_markup=markup)
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
        await db.series.insert_one({"type": "series", "title": d['title'], "year": d['year'], "category": d['category'], "language": d['language'], "thumb": d['thumb'], "seasons": seasons})
        await call.message.edit_text(f"🎉 **{d['title']}** সম্পূর্ণ সিরিজ আপলোড হয়েছে!", parse_mode="Markdown"); await state.clear()

# --- ✏️ EDIT MOVIE (কোয়ালিটি এড ও ডিলেট) ---
@dp.message(Command("editemovies"))
async def edit_mov(message: types.Message, command: CommandObject, state: FSMContext):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/editemovies RRR 2024`", parse_mode="Markdown")
    args = command.args.rsplit(' ', 1)
    title = args[0]
    movie = await db.movies.find_one({"title": {"$regex": title, "$options": "i"}})
    if not movie: return await message.answer("❌ মুভি পাওয়া যায়নি!")
    
    await state.update_data(m_id=movie['_id'], title=movie['title'])
    kb = [[InlineKeyboardButton(text=f"🗑 Delete {q['res']}", callback_data=f"delq_{i}")] for i, q in enumerate(movie.get('qualities', []))]
    kb.append([InlineKeyboardButton(text="➕ Add New Quality", callback_data="addq_new")])
    await message.answer(f"🎬 **{movie['title']}** এডিট প্যানেল:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")
    await state.set_state(EditMovieState.select_action)

@dp.callback_query(EditMovieState.select_action)
async def edit_m_action(call: types.CallbackQuery, state: FSMContext):
    d = await state.get_data()
    action = call.data
    if action.startswith("delq_"):
        index = int(action.split('_')[1])
        movie = await db.movies.find_one({"_id": d['m_id']})
        quals = movie.get('qualities', [])
        if 0 <= index < len(quals):
            quals.pop(index)
            await db.movies.update_one({"_id": d['m_id']}, {"$set": {"qualities": quals}})
            await call.message.edit_text("✅ কোয়ালিটি ডিলেট করা হয়েছে!")
            await state.clear()
    elif action == "addq_new":
        await call.message.edit_text("📺 নতুন কোয়ালিটি দিন (উদাঃ 1080p):")
        await state.set_state(EditMovieState.res)

@dp.message(EditMovieState.res)
async def em_res(message: types.Message, state: FSMContext): await state.update_data(res=message.text); await message.answer("🔗 লিংক দিন:"); await state.set_state(EditMovieState.link)
@dp.message(EditMovieState.link)
async def em_link(message: types.Message, state: FSMContext): await state.update_data(link=message.text); await message.answer("💾 সাইজ দিন:"); await state.set_state(EditMovieState.size)
@dp.message(EditMovieState.size)
async def em_save(message: types.Message, state: FSMContext):
    d = await state.get_data()
    new_q = {"res": d['res'], "link": d['link'], "size": message.text}
    await db.movies.update_one({"_id": d['m_id']}, {"$push": {"qualities": new_q}})
    await message.answer("✅ নতুন কোয়ালিটি এড করা হয়েছে!"); await state.clear()

# --- ✏️ EDIT SERIES (সিজন/এপিসোড এড) ---
@dp.message(Command("editeseries"))
async def edit_ser(message: types.Message, command: CommandObject, state: FSMContext):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/editeseries Batchlor Point`", parse_mode="Markdown")
    series = await db.series.find_one({"title": {"$regex": command.args, "$options": "i"}})
    if not series: return await message.answer("❌ সিরিজ পাওয়া যায়নি!")
    
    await state.update_data(s_id=series['_id'])
    kb = [[InlineKeyboardButton(text="➕ Add New Season / Episode", callback_data="add_s_ep")]]
    await message.answer(f"🎬 **{series['title']}** এডিট প্যানেল:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")
    await state.set_state(EditSeriesState.select_action)

@dp.callback_query(EditSeriesState.select_action)
async def edit_s_action(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("🔢 কোন সিজনে এড করবেন? (উদাঃ 1):"); await state.set_state(EditSeriesState.s_num)

@dp.message(EditSeriesState.s_num)
async def es_snum(message: types.Message, state: FSMContext): await state.update_data(s_num=message.text); await message.answer("🔢 এপিসোড নাম্বার দিন:"); await state.set_state(EditSeriesState.e_num)
@dp.message(EditSeriesState.e_num)
async def es_enum(message: types.Message, state: FSMContext): await state.update_data(e_num=message.text, cur_quals=[]); await message.answer("📺 কোয়ালিটি দিন:"); await state.set_state(EditSeriesState.res)
@dp.message(EditSeriesState.res)
async def es_res(message: types.Message, state: FSMContext): await state.update_data(res=message.text); await message.answer("🔗 লিংক দিন:"); await state.set_state(EditSeriesState.link)
@dp.message(EditSeriesState.link)
async def es_link(message: types.Message, state: FSMContext): await state.update_data(link=message.text); await message.answer("💾 সাইজ দিন:"); await state.set_state(EditSeriesState.size)
@dp.message(EditSeriesState.size)
async def es_save(message: types.Message, state: FSMContext):
    d = await state.get_data()
    new_q = {"res": d['res'], "link": d['link'], "size": message.text}
    
    # Update nested dictionary field dynamically
    field_path = f"seasons.{d['s_num']}.{d['e_num']}"
    await db.series.update_one({"_id": d['s_id']}, {"$push": {field_path: new_q}})
    await message.answer(f"✅ সিজন {d['s_num']} এপিসোড {d['e_num']} এ কোয়ালিটি এড হয়েছে!"); await state.clear()

# --- 🛠 OTHER MANAGEMENT COMMANDS (Only Admin) ---
@dp.message(Command("deletedMovies"))
async def del_movie(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/deletedMovies RRR`", parse_mode="Markdown")
    res = await db.movies.delete_many({"title": {"$regex": command.args, "$options": "i"}})
    await message.answer(f"✅ {res.deleted_count} টি মুভি ডিলেট হয়েছে।")

@dp.message(Command("deleteseries"))
async def del_series(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/deleteseries Batchlor Point`", parse_mode="Markdown")
    res = await db.series.delete_many({"title": {"$regex": command.args, "$options": "i"}})
    await message.answer(f"✅ {res.deleted_count} টি সিরিজ ডিলেট হয়েছে।")

@dp.message(Command("setcategory"))
async def set_cat(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/setcategory Action`", parse_mode="Markdown")
    await db.settings.update_one({"type": "categories"}, {"$addToSet": {"list": command.args}}, upsert=True)
    await message.answer(f"✅ Category '{command.args}' Added.")

@dp.message(Command("deletecategory"))
async def del_cat(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/deletecategory Action`", parse_mode="Markdown")
    await db.settings.update_one({"type": "categories"}, {"$pull": {"list": command.args}})
    await message.answer(f"✅ Category '{command.args}' Deleted.")

@dp.message(Command("addzoonid"))
async def add_zoon(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/addzoonid 8234857`", parse_mode="Markdown")
    await db.settings.update_one({"type": "zoonid"}, {"$set": {"id": command.args}}, upsert=True)
    await message.answer(f"✅ Zoon ID ({command.args}) Saved for Ads.")

@dp.message(Command("deletezoonid"))
async def del_zoon(message: types.Message):
    if not is_admin(message.from_user.id): return
    await db.settings.delete_one({"type": "zoonid"})
    await message.answer("✅ Zoon ID Deleted.")

@dp.message(Command("setbotname"))
async def s_name(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/setbotname MovieeLink`", parse_mode="Markdown")
    await db.settings.update_one({"type": "botname"}, {"$set": {"name": command.args}}, upsert=True)
    await message.answer(f"✅ Bot Name Updated to '{command.args}'.")

@dp.message(Command("deletebotname"))
async def d_name(message: types.Message):
    if not is_admin(message.from_user.id): return
    await db.settings.delete_one({"type": "botname"})
    await message.answer("✅ Bot Name Deleted.")

@dp.message(Command("setsite"))
async def s_site(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/setsite website.com`", parse_mode="Markdown")
    await db.settings.update_one({"type": "site"}, {"$set": {"url": command.args}}, upsert=True)
    await message.answer("✅ Site Saved.")

@dp.message(Command("deletesite"))
async def d_site(message: types.Message):
    if not is_admin(message.from_user.id): return
    await db.settings.delete_one({"type": "site"})
    await message.answer("✅ Site Deleted.")

@dp.message(Command("addpromote"))
async def p_ad(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/addpromote Join Channel!`", parse_mode="Markdown")
    await db.settings.update_one({"type": "promo"}, {"$set": {"text": command.args}}, upsert=True)
    await message.answer("✅ Promote Message Added.")

@dp.message(Command("deletepromote"))
async def dp_ad(message: types.Message):
    if not is_admin(message.from_user.id): return
    await db.settings.delete_one({"type": "promo"})
    await message.answer("✅ Promote Message Deleted.")

@dp.message(Command("addredeem"))
async def add_redeem(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/addredeem 1day 10`", parse_mode="Markdown")
    args = command.args.split()
    count = int(args[1]) if len(args) > 1 else 1
    codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(count)]
    await db.redeems.insert_many([{"code": c, "dur": args[0], "used": False} for c in codes])
    await message.answer(f"✅ {count} টি কোড তৈরি হয়েছে:\n\n`" + "`\n`".join(codes) + "`", parse_mode="Markdown")

@dp.message(Command("Premiumuserlist"))
async def p_list(message: types.Message):
    if not is_admin(message.from_user.id): return
    users = await db.users.find({"is_premium": True}).to_list(100)
    msg = "💎 Premium Users:\n" + "\n".join([f"ID: `{u['uid']}`" for u in users]) if users else "No premium users found."
    await message.answer(msg, parse_mode="Markdown")

@dp.message(Command("deletepremium"))
async def d_prem(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ উদাহরণ: `/deletepremium 12345678`", parse_mode="Markdown")
    await db.users.update_one({"uid": command.args}, {"$set": {"is_premium": False}})
    await message.answer(f"✅ Premium Status Removed for {command.args}.")

# ==========================================
# 🚀 ৬. Main Runner
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True) # Bug Fix for Unresponsive bot
    
    app = web.Application()
    app.router.add_get('/', handle_webapp)
    app.router.add_get('/api/data', handle_api_data) 
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"🌐 Server running on port {port}...")
    print("🤖 Telegram Bot running with Full Admin Control & Edit Commands...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
