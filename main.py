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
WEB_APP_URL = "https://your-render-app-url.onrender.com" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client['MovieeLinkDB']

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
    <!-- Monetag Ad Script -->
    <script src="https://alwingulla.com/88/tag.min.js" data-zone="YOUR_ZONE_ID"></script>
</head>
<body class="bg-[#f4f4f5] text-gray-800 font-sans pb-20">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- 🏠 Home Page (Screenshot 8) ---
        const HomePage = ({ data }) => (
            <div className="bg-white min-h-screen relative pb-6">
                {/* Search Bar Top */}
                <div className="flex items-center gap-3 p-4 border-b border-gray-100">
                    <h1 className="text-xl font-bold text-gray-800 flex-1">Moviee <span className="bg-red-500 text-white px-2 py-0.5 rounded text-sm">Link</span></h1>
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-xl text-gray-500 shadow-inner">🔍</div>
                </div>

                {/* Live Banner */}
                <div className="bg-[#5a4a9c] text-white text-xs py-2 px-4 flex items-center gap-2">
                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                    <span className="font-bold">LIVE</span> 
                    <marquee className="flex-1 text-[11px]">VLC Player অথবা MX Player দিয়ে চালিয়ে দেখুন। সাউন্ড/অডিও সমস্যা হলে সমাধান হয়ে যাবে।</marquee>
                </div>

                {/* Slider */}
                <div className="flex overflow-x-auto gap-4 p-4 snap-x hide-scrollbar mt-2">
                    {data.sliders.length > 0 ? data.sliders.map((img, i) => (
                        <img key={i} src={img} className="w-[85vw] h-48 object-cover rounded-2xl snap-center shrink-0 shadow-md" alt="Slider" />
                    )) : (
                        <img src="https://i.ibb.co/L5hY8mP/photo-2024-05-12.jpg" className="w-[85vw] h-48 object-cover rounded-2xl snap-center shrink-0 shadow-md" alt="Default Slider" />
                    )}
                </div>

                {/* Movie List Dynamic */}
                <div className="p-4 space-y-5">
                    {data.movies.map((m, i) => (
                        <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden relative">
                            <img src={m.thumb || "https://i.ibb.co/3sZq1bT/movie-thumb.jpg"} className="w-full h-44 object-cover" />
                            <div className="p-3">
                                <h3 className="font-bold text-lg text-gray-800">{m.title}</h3>
                                <p className="text-xs text-gray-500 mt-1">{m.year} • {m.language} • {m.category}</p>
                            </div>
                            <button className="absolute bottom-3 right-3 bg-red-500 text-white px-5 py-1.5 rounded-full text-xs font-bold shadow-md">Watch Now</button>
                        </div>
                    ))}
                </div>

                {/* Floating Search */}
                <button className="fixed bottom-24 right-4 w-14 h-14 bg-white border border-gray-200 rounded-full shadow-xl flex items-center justify-center text-2xl z-40">
                    🔍
                </button>
            </div>
        );

        // --- 🛠 Smart Tools (Screenshots 1, 2, 3) ---
        const SmartTools = () => {
            const ToolCard = ({ icon, title, desc, badge, badgeColor }) => (
                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 relative">
                    {badge && <span className={`absolute top-0 right-0 text-white text-[9px] px-2 py-1 rounded-bl-xl rounded-tr-xl font-bold ${badgeColor || 'bg-teal-400'}`}>{badge}</span>}
                    <div className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-2xl mb-3 shadow-inner">{icon}</div>
                    <h3 className="text-sm font-bold text-gray-800">{title}</h3>
                    <p className="text-[10px] text-gray-400 mt-1 leading-tight">{desc}</p>
                </div>
            );

            return (
                <div className="p-4 bg-[#f8f9fe] min-h-screen">
                    <div className="flex flex-col items-center mb-6 mt-2">
                        <h2 className="text-xl font-bold text-indigo-600 flex items-center gap-2">🛠 Smart Tools</h2>
                        <p className="text-xs text-gray-400">All the essential tools in one place ✨</p>
                    </div>
                    <input type="text" placeholder="🔍 Search tools..." className="w-full p-3.5 rounded-xl border border-gray-200 text-sm mb-6 outline-none shadow-sm" />
                    
                    {/* Stats */}
                    <div className="flex gap-2 mb-6">
                        <div className="flex-1 bg-white p-3 rounded-xl text-center shadow-sm border border-gray-50"><div className="text-2xl font-bold text-indigo-600">20</div><div className="text-[10px] text-gray-400">Total Tools</div></div>
                        <div className="flex-1 bg-white p-3 rounded-xl text-center shadow-sm border border-gray-50"><div className="text-2xl font-bold text-blue-500">7</div><div className="text-[10px] text-gray-400">Newly added</div></div>
                        <div className="flex-1 bg-white p-3 rounded-xl text-center shadow-sm border border-gray-50"><div className="text-2xl font-bold text-green-500">100%</div><div className="text-[10px] text-gray-400">Free to use</div></div>
                    </div>

                    <h3 className="font-bold text-gray-800 mb-3 text-sm flex items-center gap-1">🔥 Popular Tools</h3>
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <ToolCard icon="🎂" title="Age Calculator" desc="Calculate your exact age" />
                        <ToolCard icon="⚖️" title="BMI Calculator" desc="Calculate your Body Mass Index" />
                        <ToolCard icon="💱" title="Currency Converter" desc="Convert currencies easily" />
                        <ToolCard icon="💘" title="Love Match" desc="Test your love compatibility" />
                    </div>

                    <h3 className="font-bold text-gray-800 mb-3 text-sm flex items-center gap-1">🛡 Utility Tools</h3>
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <ToolCard icon="🔐" title="Password Generator" desc="Generate strong passwords" />
                        <ToolCard icon="🩸" title="Blood Group Finder" desc="Learn about blood groups" />
                        <ToolCard icon="📱" title="QR Code Generator" desc="Create a QR for any link" />
                        <ToolCard icon="🎲" title="Random Picker" desc="Pick a random item" />
                    </div>

                    <h3 className="font-bold text-gray-800 mb-3 text-sm flex items-center gap-1">⚡ Exclusive Tools</h3>
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <ToolCard icon="✨" title="Stylish Text Maker" desc="Create text in stylish fonts" />
                        <ToolCard icon="📿" title="Tasbih Counter" desc="Count with a digital tasbih" />
                        <ToolCard icon="🌍" title="Time Zone Converter" desc="Compare times around the world" />
                    </div>

                    <h3 className="font-bold text-gray-800 mb-3 text-sm flex items-center gap-1">🧰 More Useful Tools</h3>
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <ToolCard icon="📏" title="Unit Converter" desc="Convert length, weight, temp" badge="NEW" />
                        <ToolCard icon="📊" title="Percentage Calculator" desc="Calculate any percentage" badge="NEW" />
                        <ToolCard icon="💰" title="EMI Calculator" desc="Calculate your monthly loan" badge="NEW" />
                        <ToolCard icon="📅" title="Date Difference" desc="Count days between two dates" badge="NEW" />
                        <ToolCard icon="🔠" title="Text Case" desc="Change case & count words" badge="NEW" />
                        <ToolCard icon="🕌" title="Zakat Calculator" desc="Calculate your Zakat easily" badge="NEW" />
                        <ToolCard icon="🎨" title="Color Picker" desc="Get HEX, RGB, HSL codes" badge="NEW" />
                    </div>

                    <h3 className="font-bold text-gray-800 mb-3 text-sm flex items-center gap-1">🌟 More Tools</h3>
                    <div className="grid grid-cols-2 gap-3">
                        <ToolCard icon="🔗" title="Link Shortener" desc="Shorten long links" badge="SOON" badgeColor="bg-red-500" />
                        <ToolCard icon="🎬" title="Movie Recommendation" desc="Find movies you'll love" badge="SOON" badgeColor="bg-red-500" />
                    </div>
                </div>
            );
        };

        // --- 🎬 Movie Details (Screenshot 5 - 15s Monetag Ad) ---
        const MovieDetails = ({ movie }) => {
            const [adTimer, setAdTimer] = useState(0);
            const [isAdRunning, setIsAdRunning] = useState(false);
            const [isUnlocked, setIsUnlocked] = useState(false);

            const handleDownloadClick = () => {
                if (isUnlocked) { alert("Download Linked Unlocked! Ready to download."); return; }
                
                // Monetag Popunder Call
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
                        <img src="https://i.ibb.co/3sZq1bT/movie-thumb.jpg" className="w-full h-64 object-cover" />
                        <span className="absolute top-3 left-3 bg-yellow-400 text-black px-2 py-0.5 text-xs font-bold rounded shadow">HD</span>
                    </div>
                    <div className="p-4">
                        <h1 className="text-xl font-bold text-gray-900">{movie?.title || "Shada Private Natok"}</h1>
                        
                        <div className="flex justify-around my-6 text-center text-sm font-medium text-gray-500">
                            <div><span className="block text-2xl text-red-500 mb-1">❤️</span> 3 Like</div>
                            <div><span className="block text-2xl text-blue-400 mb-1">⬇️</span> 82 Download</div>
                            <div><span className="block text-2xl text-gray-600 mb-1">💬</span> 0 Comments</div>
                        </div>

                        <button onClick={handleDownloadClick} disabled={isAdRunning} className={`w-full py-3.5 rounded-xl font-bold mb-3 transition-all shadow-sm ${isUnlocked ? 'bg-green-500 text-white' : 'bg-[#fff1ec] text-[#e65c2a] border border-[#ffdfd4]'}`}>
                            {isAdRunning ? `⏳ Please wait... ${adTimer}s (Ad is showing)` : isUnlocked ? '✅ Download Now' : '💡 Tap the button below to download easily'}
                        </button>

                        <button className="w-full bg-[#1b55e2] text-white py-3 rounded-xl font-medium mb-6 text-sm shadow-md">
                            ❓ Need help? Watch the tutorial
                        </button>
                        
                        <div className="flex gap-3 text-sm font-medium mb-6">
                            <button className="flex-1 border border-pink-200 text-pink-500 py-3 rounded-full flex justify-center items-center gap-1 bg-pink-50/30">♡ Like</button>
                            <button className="flex-[1.5] bg-black text-white py-3 rounded-full flex justify-center items-center gap-1 shadow-lg">⬇ Download</button>
                            <button className="flex-1 border border-orange-200 text-orange-500 py-3 rounded-full flex justify-center items-center gap-1 bg-orange-50/30">🔖 Save</button>
                        </div>
                        
                        <div className="bg-yellow-50 border border-yellow-100 p-4 rounded-xl flex justify-between items-center mb-6">
                            <span className="text-gray-600 text-sm">Rate it: <span className="text-gray-300 text-lg ml-1">☆☆☆☆☆</span></span>
                            <span className="text-yellow-500 font-bold text-sm flex items-center gap-1">★ 4.0 (1)</span>
                        </div>

                        <h3 className="font-bold text-gray-800 mb-4 border-b pb-2">Comments (0)</h3>
                        <div className="flex gap-2">
                            <input type="text" placeholder="Add a public comment..." className="flex-1 bg-gray-50 border border-gray-200 rounded-full px-4 py-2 text-sm outline-none" />
                            <button className="w-10 h-10 bg-black text-white rounded-full flex items-center justify-center">➤</button>
                        </div>
                    </div>
                </div>
            );
        };

        // --- 📱 Main App Component ---
        const App = () => {
            const [page, setPage] = useState('home');
            const [showWelcome, setShowWelcome] = useState(true);
            const [appData, setAppData] = useState({ movies: [], sliders: [] });

            useEffect(() => {
                if(window.Telegram?.WebApp) window.Telegram.WebApp.expand();
                // Fetch dynamic data from python backend
                fetch('/api/data').then(r => r.json()).then(data => setAppData(data));
            }, []);

            return (
                <div className="relative">
                    {/* Welcome Popup (Screenshot 4) */}
                    {showWelcome && (
                        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
                            <div className="bg-white rounded-3xl p-7 text-center w-full max-w-sm shadow-2xl relative">
                                <h2 className="text-2xl font-extrabold mb-4 text-gray-900 leading-tight">👋 Welcome to<br/>MovieeLink Bot!</h2>
                                <div className="text-left text-gray-600 text-sm space-y-4 mb-8">
                                    <p className="flex gap-2"><span className="text-lg">🎬</span> <span>এখানে আপনি হাজারো Movie, Web Series, Drama ও Anime দেখতে পারবেন।</span></p>
                                    <p className="flex gap-2"><span className="text-lg">🔍</span> <span>আপনার পছন্দের Movie খুঁজতে Search ব্যবহার করুন।</span></p>
                                    <p className="flex gap-2"><span className="text-lg">🎵</span> <span>ভিডিওতে সাউন্ড বা অডিও ট্র্যাক সংক্রান্ত সমস্যা হলে, ভিডিওটি ডাউনলোড করে VLC Player অথবা MX Player দিয়ে প্লে করুন।</span></p>
                                    <p className="flex gap-2"><span className="text-lg">📩</span> <span>কোনো Movie খুঁজে না পেলে Movie Request পাঠান। আমরা যত দ্রুত সম্ভব যোগ করার চেষ্টা করব।</span></p>
                                    <p className="text-center font-bold text-gray-800 mt-2">🍿 Happy Watching! ❤️</p>
                                </div>
                                <button onClick={() => setShowWelcome(false)} className="bg-[#6c5ce7] text-white px-10 py-3 rounded-xl font-bold shadow-lg shadow-indigo-200">OK ✅</button>
                            </div>
                        </div>
                    )}

                    {page === 'home' && <HomePage data={appData} />}
                    {page === 'tools' && <SmartTools />}
                    {page === 'details' && <MovieDetails movie={appData.movies[0]} />}

                    {/* Bottom Navigation */}
                    <div className="fixed bottom-0 w-full bg-[#f4f4f5] border-t border-gray-200 flex justify-between px-6 py-2.5 text-[10px] text-gray-500 font-medium z-40 shadow-[0_-10px_15px_rgba(0,0,0,0.03)]">
                        <button onClick={() => setPage('home')} className={`flex flex-col items-center ${page==='home'?'text-red-500':''}`}><span className="text-[22px] mb-0.5">🏠</span> Home</button>
                        <button onClick={() => setPage('details')} className={`flex flex-col items-center ${page==='details'?'text-red-500':''}`}><span className="text-[22px] mb-0.5">🔖</span> Favorite</button>
                        <button onClick={() => setPage('tools')} className={`flex flex-col items-center ${page==='tools'?'text-red-500':''}`}><span className="text-[22px] mb-0.5">🔧</span> Tools</button>
                        <button className="flex flex-col items-center"><span className="text-[22px] mb-0.5">📅</span> Upcoming</button>
                        <button className="flex flex-col items-center"><span className="text-lg bg-pink-200 text-pink-600 rounded-full px-1.5 py-0.5 mb-1 mt-0.5 border border-pink-300">TE</span> Setting</button>
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
# 🌐 ৩. ওয়েব সার্ভার এপিআই (React এর জন্য)
# ==========================================
async def handle_webapp(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_api_data(request):
    movies = await db.movies.find().sort('_id', -1).limit(10).to_list(10)
    sliders_doc = await db.settings.find_one({"type": "sliders"})
    sliders = sliders_doc['list'] if sliders_doc else []
    for m in movies: m['_id'] = str(m['_id'])
    return web.json_response({"movies": movies, "sliders": sliders})

# ==========================================
# 🤖 ৪. বট লজিক এবং স্টেটমেশিন (Unlimited Loops)
# ==========================================
class MovieState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class SeriesState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    s_num = State(); e_num = State()
    q_res = State(); q_link = State(); q_size = State(); ask_more = State()

# --- 🎯 /start (Screenshot 6/7 Design) ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🍿 WATCH NOW", web_app=types.WebAppInfo(url=WEB_APP_URL))],
        [types.InlineKeyboardButton(text="🎁 Share Friend", switch_inline_query="Share"), types.InlineKeyboardButton(text="📡 Join All Channel", url="https://t.me/Movieelinkbo")]
    ])
    await message.answer_photo(
        photo="https://i.ibb.co/3sZq1bT/movie-thumb.jpg", 
        caption="👋 **হ্যালো THE END!**\n\n🎬 উপরের টিউটোরিয়াল ভিডিওটি অন্তত একবার দেখে নিন\n\n🍿 এখানে পাবেন নিত্য নতুন মুভি ও সিরিজ কালেকশন — দেরি না করে নিচের Watch Now বাটনে ক্লিক করো!",
        reply_markup=markup, parse_mode="Markdown"
    )

# --- 🎬 মুভি এড কমান্ড (আনলিমিটেড কোয়ালিটি লুপ) ---
@dp.message(Command("movies"))
async def add_movie(message: types.Message, state: FSMContext):
    await state.clear(); await message.answer("🎬 মুভির নাম দিন (উদাঃ RRR):"); await state.set_state(MovieState.title)

@dp.message(MovieState.title)
async def m_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text, qualities=[]); await message.answer("📅 সাল দিন (উদাঃ 2024):"); await state.set_state(MovieState.year)

@dp.message(MovieState.year)
async def m_cat(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text); await message.answer("📁 ক্যাটাগরি সিলেক্ট করুন (Action/Romance/Comedy):"); await state.set_state(MovieState.category)

@dp.message(MovieState.category)
async def m_lang(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text); await message.answer("🗣 ভাষা সিলেক্ট করুন (Bangla/Hindi/English):"); await state.set_state(MovieState.language)

@dp.message(MovieState.language)
async def m_res(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text); await message.answer("📺 কোয়ালিটি দিন (উদাঃ 720p, 1080p):"); await state.set_state(MovieState.q_res)

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
    await message.answer(f"✅ এখন পর্যন্ত {len(quals)} টি কোয়ালিটি এড হয়েছে। পরবর্তী ধাপ:", reply_markup=markup)
    await state.set_state(MovieState.ask_more)

@dp.callback_query(MovieState.ask_more)
async def m_save(call: types.CallbackQuery, state: FSMContext):
    if call.data == "m_more":
        await call.message.edit_text("📺 নতুন কোয়ালিটি দিন (উদাঃ 480p):"); await state.set_state(MovieState.q_res)
    else:
        d = await state.get_data()
        await db.movies.insert_one({"type": "movie", "title": d['title'], "year": d['year'], "category": d['category'], "language": d['language'], "qualities": d['qualities']})
        await call.message.edit_text(f"🎉 **{d['title']}** ডাটাবেসে সেভ হয়েছে!", parse_mode="Markdown"); await state.clear()

# --- 🎥 সিরিজ এড কমান্ড (আনলিমিটেড সিজন, এপিসোড ও কোয়ালিটি লুপ) ---
@dp.message(Command("addseries"))
async def add_series(message: types.Message, state: FSMContext):
    await state.clear(); await state.update_data(seasons={}); await message.answer("🎬 সিরিজের নাম দিন (উদাঃ Batchlor Point):"); await state.set_state(SeriesState.title)

@dp.message(SeriesState.title)
async def s_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text); await message.answer("📅 সাল দিন (উদাঃ 2026):"); await state.set_state(SeriesState.year)

@dp.message(SeriesState.year)
async def s_cat(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text); await message.answer("📁 ক্যাটাগরি দিন (Action/Comedy):"); await state.set_state(SeriesState.category)

@dp.message(SeriesState.category)
async def s_lang(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text); await message.answer("🗣 ভাষা দিন (Bangla):"); await state.set_state(SeriesState.language)

@dp.message(SeriesState.language)
async def s_snum(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text); await message.answer("🔢 সিজন নাম্বার দিন (উদাঃ 1):"); await state.set_state(SeriesState.s_num)

@dp.message(SeriesState.s_num)
async def s_ep(message: types.Message, state: FSMContext):
    await state.update_data(cur_s=message.text); await message.answer(f"সিজন {message.text} এর 🔢 এপিসোড নাম্বার দিন (উদাঃ 1):"); await state.set_state(SeriesState.e_num)

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
    await message.answer(f"✅ সিজন {d['cur_s']} | এপিসোড {d['cur_e']} | কোয়ালিটি {len(q)} টি এড হয়েছে।\nপরবর্তী ধাপ সিলেক্ট করুন:", reply_markup=markup)
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
        await db.series.insert_one({"type": "series", "title": d['title'], "year": d['year'], "category": d['category'], "language": d['language'], "seasons": seasons})
        await call.message.edit_text(f"🎉 **{d['title']}** সম্পূর্ণ সিরিজ সেভ হয়েছে!", parse_mode="Markdown"); await state.clear()

# --- 🛠 অন্যান্য সকল কমান্ড (এরর হ্যান্ডেলিং সহ) ---
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

@dp.message(Command("editemovies"))
async def edit_mov(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/editemovies RRR 2024`", parse_mode="Markdown")
    await message.answer(f"✅ Edit Data for '{command.args}' triggered. Panel feature coming soon.")

@dp.message(Command("editeseries"))
async def edit_ser(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/editeseries Batchlor Point 2026`", parse_mode="Markdown")
    await message.answer(f"✅ Edit Data for '{command.args}' triggered. Panel feature coming soon.")

@dp.message(Command("setcategory"))
async def set_cat(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/setcategory Action`", parse_mode="Markdown")
    await db.settings.update_one({"type": "categories"}, {"$addToSet": {"list": command.args}}, upsert=True)
    await message.answer(f"✅ Category '{command.args}' Added.")

@dp.message(Command("deletecategory"))
async def del_cat(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/deletecategory Action`", parse_mode="Markdown")
    await db.settings.update_one({"type": "categories"}, {"$pull": {"list": command.args}})
    await message.answer(f"✅ Category '{command.args}' Deleted.")

@dp.message(Command("addzoonid"))
async def add_zoon(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/addzoonid 8234857`", parse_mode="Markdown")
    await db.settings.update_one({"type": "zoonid"}, {"$set": {"id": command.args}}, upsert=True)
    await message.answer(f"✅ Zoon ID ({command.args}) Saved for Ads.")

@dp.message(Command("deletezoonid"))
async def del_zoon(message: types.Message):
    await db.settings.delete_one({"type": "zoonid"})
    await message.answer("✅ Zoon ID Deleted.")

@dp.message(Command("addredeem"))
async def add_redeem(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/addredeem 1day 10`", parse_mode="Markdown")
    args = command.args.split()
    count = int(args[1]) if len(args) > 1 else 1
    codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(count)]
    await db.redeems.insert_many([{"code": c, "dur": args[0], "used": False} for c in codes])
    await message.answer(f"✅ {count} টি কোড তৈরি হয়েছে:\n\n`" + "`\n`".join(codes) + "`", parse_mode="Markdown")

@dp.message(Command("Premiumuserlist"))
async def p_list(message: types.Message): 
    users = await db.users.find({"is_premium": True}).to_list(100)
    msg = "💎 Premium Users:\n" + "\n".join([f"ID: `{u['uid']}`" for u in users]) if users else "No premium users found."
    await message.answer(msg, parse_mode="Markdown")

@dp.message(Command("deletepremium"))
async def d_prem(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/deletepremium 12345678`", parse_mode="Markdown")
    await db.users.update_one({"uid": command.args}, {"$set": {"is_premium": False}})
    await message.answer(f"✅ Premium Status Removed for {command.args}.")

@dp.message(Command("promotead"))
async def p_ad(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/promotead Join our new channel!`", parse_mode="Markdown")
    await db.settings.update_one({"type": "promo"}, {"$set": {"text": command.args}}, upsert=True)
    await message.answer("✅ Promote Ad Added.")

@dp.message(Command("deletesite"))
async def d_site(message: types.Message):
    await db.settings.delete_one({"type": "site"})
    await message.answer("✅ Site Data Deleted.")

@dp.message(Command("setbotname"))
async def s_name(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/setbotname MovieeLink`", parse_mode="Markdown")
    await db.settings.update_one({"type": "botname"}, {"$set": {"name": command.args}}, upsert=True)
    await message.answer(f"✅ Bot Name Updated to '{command.args}'.")

@dp.message(Command("addslider"))
async def add_slider(message: types.Message, command: CommandObject):
    if not command.args: return await message.answer("⚠️ ভুল ফরমেট!\nউদাহরণ: `/addslider https://link.com/img.jpg`", parse_mode="Markdown")
    await db.settings.update_one({"type": "sliders"}, {"$addToSet": {"list": command.args}}, upsert=True)
    await message.answer("✅ Slider Image Added successfully!")

# ==========================================
# 🚀 ৫. Main Runner (বট ও ওয়েবসাইট একসাথে)
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    
    app = web.Application()
    app.router.add_get('/', handle_webapp)
    app.router.add_get('/api/data', handle_api_data) 
    
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    print(f"🌐 Web Server running on port {port}...")
    await site.start()
    
    print("🤖 Telegram Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
