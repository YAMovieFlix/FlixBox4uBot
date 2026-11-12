import asyncio
import logging
import random
import string
import os
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# ==========================================
# ⚙️ ১. কনফিগারেশন
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9219855483:AAH9ZrxFejeC_j9X697I_UOGSlnneH1_bSs")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://akash:akash@cluster0.etisrpx.mongodb.net/?appName=Cluster0")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://flixbox4ubot.onrender.com")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7120801813"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client['MovieeLinkDB']

def is_admin(user_id):
    return user_id == ADMIN_ID

# ==========================================
# 🌐 ২. ফ্রন্টএন্ড ওয়েব অ্যাপ (React + Tailwind UI)
# ==========================================
HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Moviee Link</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-[#f8f9fa] text-gray-800 font-sans pb-24 select-none">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- 1. HOME TAB ---
        const HomePage = ({ data, onSelect, onSearch, searchQuery }) => {
            const filteredItems = data.items.filter(item => 
                item.title.toLowerCase().includes(searchQuery.toLowerCase())
            );

            return (
                <div className="min-h-screen">
                    {/* Header */}
                    <div className="bg-white p-4 sticky top-0 z-30 shadow-sm flex items-center justify-between">
                        <h1 className="text-xl font-bold tracking-tight text-gray-800">
                            {data.botname || "Moviee"} <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded font-extrabold uppercase">Link</span>
                        </h1>
                        <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-bold flex items-center gap-1">
                            🔴 LIVE
                        </span>
                    </div>

                    {/* Promo Notification */}
                    {data.promo && (
                        <div className="bg-red-50 text-red-700 text-xs py-2 px-4 border-b border-red-100 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
                            <marquee className="font-medium">{data.promo}</marquee>
                        </div>
                    )}

                    {/* Search Bar */}
                    <div className="p-4 pb-2">
                        <div className="relative flex items-center">
                            <span className="absolute left-4 text-gray-400">🔍</span>
                            <input 
                                type="text"
                                placeholder="Search movies, web series..."
                                value={searchQuery}
                                onChange={(e) => onSearch(e.target.value)}
                                className="w-full pl-11 pr-4 py-2.5 bg-white border border-gray-200 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-red-400 text-sm"
                            />
                        </div>
                    </div>

                    {/* Sliders */}
                    {data.sliders && data.sliders.length > 0 && (
                        <div className="flex overflow-x-auto gap-3.5 px-4 py-2 snap-x hide-scrollbar">
                            {data.sliders.map((img, i) => (
                                <img key={i} src={img} className="w-[85vw] h-44 object-cover rounded-2xl snap-center shrink-0 shadow-md border border-gray-100" />
                            ))}
                        </div>
                    )}

                    {/* Content List */}
                    <div className="p-4 space-y-4">
                        <div className="flex items-center justify-between">
                            <h2 className="font-bold text-gray-800 text-md flex items-center gap-1.5">🔥 Recent Releases</h2>
                            <span className="text-xs text-gray-400">{filteredItems.length} items</span>
                        </div>

                        {filteredItems.length === 0 && (
                            <div className="text-center py-12 text-gray-400">
                                📭 কোনো মুভি বা সিরিজ পাওয়া যায়নি!
                            </div>
                        )}

                        {filteredItems.map((item, idx) => (
                            <div 
                                key={idx} 
                                onClick={() => onSelect(item)}
                                className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 active:scale-[0.98] transition cursor-pointer"
                            >
                                <div className="relative">
                                    <img src={item.thumb} alt={item.title} className="w-full h-48 object-cover" />
                                    <span className="absolute top-2 right-2 bg-black/60 text-yellow-400 text-[10px] font-bold px-2 py-0.5 rounded shadow backdrop-blur-sm">HD</span>
                                    <span className="absolute bottom-2 left-2 bg-black/60 text-white text-[11px] font-medium px-2 py-0.5 rounded backdrop-blur-sm">
                                        ⭐ {item.rating || "4.5"}
                                    </span>
                                </div>
                                <div className="p-3.5 flex justify-between items-center">
                                    <div>
                                        <h3 className="font-bold text-gray-800 text-sm">{item.title}</h3>
                                        <p className="text-[11px] text-gray-500 mt-0.5">
                                            <span className={item.type === 'movie' ? 'text-blue-500 font-bold' : 'text-purple-600 font-bold'}>
                                                {item.type === 'movie' ? 'MOVIE' : 'SERIES'}
                                            </span> • {item.year} • {item.language || "Bangla"}
                                        </p>
                                    </div>
                                    <button className="bg-red-500 hover:bg-red-600 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-sm">
                                        Watch
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            );
        };

        // --- 2. DETAILS PAGE (Screen 4 Layout) ---
        const DetailsPage = ({ item, goBack, zoonid, onToggleFav, isFav }) => {
            const [unlocked, setUnlocked] = useState(false);
            const [loadingAd, setLoadingAd] = useState(false);
            const [timer, setTimer] = useState(10);
            const [likes, setLikes] = useState(item.likes || 12);
            const [hasLiked, setHasLiked] = useState(false);
            const [downloads, setDownloads] = useState(item.downloads || 85);
            const [comments, setComments] = useState(item.comments || []);
            const [commentInput, setCommentInput] = useState('');
            const [rating, setRating] = useState(4);

            const handleUnlock = () => {
                if (unlocked) return;
                setLoadingAd(true);
                let count = 10;
                setTimer(count);
                const inter = setInterval(() => {
                    count -= 1;
                    setTimer(count);
                    if (count <= 0) {
                        clearInterval(inter);
                        setLoadingAd(false);
                        setUnlocked(true);
                        setDownloads(d => d + 1);
                    }
                }, 1000);
            };

            const handleLike = () => {
                if (!hasLiked) {
                    setLikes(likes + 1);
                    setHasLiked(true);
                } else {
                    setLikes(likes - 1);
                    setHasLiked(false);
                }
            };

            const addComment = () => {
                if (!commentInput.trim()) return;
                setComments([...comments, { text: commentInput, date: "Just now" }]);
                setCommentInput('');
            };

            return (
                <div className="bg-white min-h-screen pb-16">
                    {/* Top Bar */}
                    <div className="p-3.5 flex items-center justify-between border-b border-gray-100 sticky top-0 bg-white/95 backdrop-blur z-20">
                        <button onClick={goBack} className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-700 font-bold">←</button>
                        <h2 className="font-bold text-gray-800 text-sm">Video Details</h2>
                        <button onClick={() => onToggleFav(item)} className="text-xl">
                            {isFav ? '❤️' : '🤍'}
                        </button>
                    </div>

                    {/* Thumbnail banner */}
                    <div className="relative">
                        <img src={item.thumb} className="w-full h-64 object-cover" />
                        <span className="absolute top-3 left-3 bg-yellow-400 text-black px-2 py-0.5 text-xs font-black rounded shadow">HD</span>
                    </div>

                    {/* Title & Info */}
                    <div className="p-4 border-b border-gray-100">
                        <h1 className="text-lg font-bold text-gray-900">{item.title}</h1>
                        <p className="text-xs text-gray-500 mt-1">{item.year} | {item.category || "Drama"} | {item.language || "Bangla"}</p>

                        {/* Counters */}
                        <div className="flex justify-around items-center mt-5 py-2.5 bg-gray-50 rounded-2xl border border-gray-100 text-center">
                            <div onClick={handleLike} className="cursor-pointer">
                                <span className="text-lg">{hasLiked ? '❤️' : '🤍'}</span>
                                <p className="text-xs font-bold text-gray-700">{likes}</p>
                                <p className="text-[10px] text-gray-400">Like</p>
                            </div>
                            <div className="h-6 w-[1px] bg-gray-200"></div>
                            <div>
                                <span className="text-lg">⬇️</span>
                                <p className="text-xs font-bold text-gray-700">{downloads}</p>
                                <p className="text-[10px] text-gray-400">Download</p>
                            </div>
                            <div className="h-6 w-[1px] bg-gray-200"></div>
                            <div>
                                <span className="text-lg">💬</span>
                                <p className="text-xs font-bold text-gray-700">{comments.length}</p>
                                <p className="text-[10px] text-gray-400">Comments</p>
                            </div>
                        </div>

                        {/* Action buttons */}
                        <div className="mt-4 space-y-2">
                            <div className="bg-amber-50 border border-amber-200 rounded-xl p-2.5 text-center text-xs text-amber-800 font-medium">
                                💡 Tap the button below to download easily
                            </div>

                            <a href="https://t.me/" target="_blank" className="block w-full py-2.5 text-center text-xs font-bold text-white bg-blue-500 rounded-xl shadow-sm">
                                ❓ Need help? Watch the tutorial
                            </a>

                            {!unlocked ? (
                                <button 
                                    onClick={handleUnlock}
                                    disabled={loadingAd}
                                    className={`w-full py-3.5 rounded-xl font-bold text-sm shadow-md transition ${loadingAd ? 'bg-orange-100 text-orange-600' : 'bg-red-500 text-white active:scale-95'}`}
                                >
                                    {loadingAd ? `⏳ Unlocking link... ${timer}s` : '📥 Download / Watch Now'}
                                </button>
                            ) : (
                                <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-2xl">
                                    <h4 className="font-bold text-emerald-800 text-xs mb-2">✅ Links are Ready:</h4>
                                    {item.type === 'movie' && item.qualities && item.qualities.map((q, idx) => (
                                        <a key={idx} href={q.link} target="_blank" className="block text-center bg-emerald-600 text-white font-bold text-xs py-2.5 rounded-xl mb-2 shadow-sm">
                                            ⬇️ Download {q.res} ({q.size})
                                        </a>
                                    ))}

                                    {item.type === 'series' && item.seasons && Object.keys(item.seasons).map(sNum => (
                                        <div key={sNum} className="mb-3">
                                            <h5 className="font-bold text-xs text-indigo-800 bg-indigo-100 p-1.5 rounded">Season {sNum}</h5>
                                            {Object.keys(item.seasons[sNum]).map(eNum => (
                                                <div key={eNum} className="mt-2 pl-2 border-l-2 border-indigo-200">
                                                    <p className="text-[11px] font-semibold text-gray-700">Episode {eNum}</p>
                                                    <div className="flex flex-wrap gap-1.5 mt-1">
                                                        {item.seasons[sNum][eNum].map((q, qi) => (
                                                            <a key={qi} href={q.link} target="_blank" className="text-[10px] bg-blue-500 text-white font-bold px-3 py-1 rounded-lg">
                                                                ⬇️ {q.res} ({q.size})
                                                            </a>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Rate it */}
                        <div className="mt-4 p-3 bg-gray-50 border border-gray-100 rounded-xl flex items-center justify-between">
                            <span className="text-xs font-semibold text-gray-700">Rate it:</span>
                            <div className="flex gap-1 text-base cursor-pointer">
                                {[1,2,3,4,5].map(st => (
                                    <span key={st} onClick={() => setRating(st)}>{st <= rating ? '⭐' : '☆'}</span>
                                ))}
                            </div>
                            <span className="text-xs font-bold text-amber-600">{rating}.0 (1)</span>
                        </div>
                    </div>

                    {/* Comments Section */}
                    <div className="p-4">
                        <h3 className="font-bold text-sm text-gray-800 mb-3">Comments ({comments.length})</h3>
                        <div className="flex gap-2">
                            <input 
                                type="text"
                                value={commentInput}
                                onChange={(e) => setCommentInput(e.target.value)}
                                placeholder="Add a public comment..."
                                className="flex-1 bg-gray-100 border border-gray-200 text-xs px-3.5 py-2 rounded-xl focus:outline-none"
                            />
                            <button onClick={addComment} className="bg-red-500 text-white text-xs px-4 py-2 rounded-xl font-bold">Post</button>
                        </div>

                        <div className="mt-4 space-y-2">
                            {comments.map((c, i) => (
                                <div key={i} className="p-2.5 bg-gray-50 rounded-xl border border-gray-100 text-xs">
                                    <p className="font-semibold text-gray-800">User #{i+1}</p>
                                    <p className="text-gray-600 mt-0.5">{c.text}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            );
        };

        // --- 3. SMART TOOLS TAB (Screen 1 & 2 Layout) ---
        const ToolsPage = () => {
            const [activeTool, setActiveTool] = useState(null);

            // Sub-tool states
            const [ageDate, setAgeDate] = useState('');
            const [calcAge, setCalcAge] = useState(null);

            const [bmiWeight, setBmiWeight] = useState('');
            const [bmiHeight, setBmiHeight] = useState('');
            const [bmiRes, setBmiRes] = useState(null);

            const [tasbih, setTasbih] = useState(0);
            const [qrText, setQrText] = useState('');

            const toolsList = [
                { id: "age", name: "Age Calculator", desc: "Calculate your exact age", icon: "🎂", tag: "Popular" },
                { id: "bmi", name: "BMI Calculator", desc: "Calculate Body Mass Index", icon: "⚖️", tag: "Popular" },
                { id: "tasbih", name: "Tasbih Counter", desc: "Count with a digital tasbih", icon: "📿", tag: "Exclusive" },
                { id: "qr", name: "QR Code Generator", desc: "Create a QR for any link", icon: "📱", tag: "Utility" },
                { id: "pwd", name: "Password Generator", desc: "Generate strong passwords", icon: "🔐", tag: "Utility" },
                { id: "date", name: "Date Difference", desc: "Count days between dates", icon: "📅", tag: "NEW" },
                { id: "emi", name: "EMI Calculator", desc: "Calculate monthly installments", icon: "💰", tag: "NEW" },
                { id: "zakat", name: "Zakat Calculator", desc: "Calculate your Zakat easily", icon: "🕌", tag: "NEW" },
            ];

            const runAge = () => {
                if (!ageDate) return;
                const diff = new Date() - new Date(ageDate);
                const years = Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
                setCalcAge(`${years} Years old`);
            };

            const runBmi = () => {
                const w = parseFloat(bmiWeight), h = parseFloat(bmiHeight) / 100;
                if (w && h) {
                    const score = (w / (h * h)).toFixed(1);
                    setBmiRes(`BMI: ${score} (${score < 18.5 ? 'Underweight' : score < 25 ? 'Normal' : 'Overweight'})`);
                }
            };

            return (
                <div className="min-h-screen p-4 pb-20">
                    <div className="flex items-center gap-2 mb-4">
                        <span className="text-xl">🛠</span>
                        <div>
                            <h1 className="text-lg font-bold text-gray-800">Smart Tools</h1>
                            <p className="text-[11px] text-gray-400">All the essential tools in one place ✨</p>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-2.5 mb-5 text-center">
                        <div className="bg-white p-3 rounded-2xl border border-gray-100 shadow-sm">
                            <h4 className="font-extrabold text-indigo-600 text-lg">20</h4>
                            <p className="text-[10px] text-gray-400">Total Tools</p>
                        </div>
                        <div className="bg-white p-3 rounded-2xl border border-gray-100 shadow-sm">
                            <h4 className="font-extrabold text-emerald-600 text-lg">7</h4>
                            <p className="text-[10px] text-gray-400">Newly added</p>
                        </div>
                        <div className="bg-white p-3 rounded-2xl border border-gray-100 shadow-sm">
                            <h4 className="font-extrabold text-rose-500 text-lg">100%</h4>
                            <p className="text-[10px] text-gray-400">Free to use</p>
                        </div>
                    </div>

                    {/* Grid list of tools */}
                    <div className="grid grid-cols-2 gap-3">
                        {toolsList.map(t => (
                            <div 
                                key={t.id} 
                                onClick={() => setActiveTool(t.id)}
                                className="bg-white p-3.5 rounded-2xl border border-gray-100 shadow-sm active:scale-95 transition cursor-pointer relative overflow-hidden"
                            >
                                <span className="absolute top-2 right-2 text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-600">
                                    {t.tag}
                                </span>
                                <div className="text-2xl mb-2">{t.icon}</div>
                                <h3 className="font-bold text-xs text-gray-800">{t.name}</h3>
                                <p className="text-[10px] text-gray-400 mt-0.5 line-clamp-1">{t.desc}</p>
                            </div>
                        ))}
                    </div>

                    {/* Active Modal / Detail for Tools */}
                    {activeTool && (
                        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                            <div className="bg-white rounded-3xl p-5 w-full max-w-sm shadow-2xl relative">
                                <button onClick={() => setActiveTool(null)} className="absolute top-4 right-4 text-gray-400 font-bold text-lg">✕</button>
                                
                                {activeTool === 'age' && (
                                    <div>
                                        <h3 className="font-bold text-sm mb-3">🎂 Age Calculator</h3>
                                        <input type="date" value={ageDate} onChange={e=>setAgeDate(e.target.value)} className="w-full p-2.5 border rounded-xl text-xs mb-3" />
                                        <button onClick={runAge} className="w-full bg-red-500 text-white font-bold py-2 rounded-xl text-xs">Calculate</button>
                                        {calcAge && <p className="mt-3 text-center font-bold text-indigo-600">{calcAge}</p>}
                                    </div>
                                )}

                                {activeTool === 'bmi' && (
                                    <div>
                                        <h3 className="font-bold text-sm mb-3">⚖️ BMI Calculator</h3>
                                        <input type="number" placeholder="Weight (kg)" value={bmiWeight} onChange={e=>setBmiWeight(e.target.value)} className="w-full p-2 border rounded-xl text-xs mb-2" />
                                        <input type="number" placeholder="Height (cm)" value={bmiHeight} onChange={e=>setBmiHeight(e.target.value)} className="w-full p-2 border rounded-xl text-xs mb-3" />
                                        <button onClick={runBmi} className="w-full bg-blue-500 text-white font-bold py-2 rounded-xl text-xs">Calculate BMI</button>
                                        {bmiRes && <p className="mt-3 text-center font-bold text-emerald-600">{bmiRes}</p>}
                                    </div>
                                )}

                                {activeTool === 'tasbih' && (
                                    <div className="text-center py-4">
                                        <h3 className="font-bold text-sm mb-4">📿 Digital Tasbih</h3>
                                        <div className="text-5xl font-black text-emerald-600 mb-6">{tasbih}</div>
                                        <div className="flex gap-2 justify-center">
                                            <button onClick={()=>setTasbih(t=>t+1)} className="bg-emerald-500 text-white font-bold px-6 py-3 rounded-2xl text-base shadow active:scale-95">Count (+)</button>
                                            <button onClick={()=>setTasbih(0)} className="bg-gray-200 text-gray-700 font-bold px-4 py-3 rounded-2xl text-xs">Reset</button>
                                        </div>
                                    </div>
                                )}

                                {activeTool === 'qr' && (
                                    <div>
                                        <h3 className="font-bold text-sm mb-3">📱 QR Code Generator</h3>
                                        <input type="text" placeholder="Enter link or text" value={qrText} onChange={e=>setQrText(e.target.value)} className="w-full p-2.5 border rounded-xl text-xs mb-3" />
                                        {qrText && (
                                            <div className="flex justify-center p-2">
                                                <img src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrText)}`} alt="QR" className="rounded-xl border" />
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTool === 'pwd' && (
                                    <div className="text-center py-2">
                                        <h3 className="font-bold text-sm mb-3">🔐 Password Generator</h3>
                                        <div className="p-3 bg-gray-100 rounded-xl font-mono text-xs select-all font-bold text-indigo-600 mb-4">
                                            {Math.random().toString(36).slice(-10) + "!A8@"}
                                        </div>
                                        <button onClick={()=>setActiveTool('pwd')} className="bg-indigo-600 text-white text-xs font-bold py-2 px-5 rounded-xl">Generate New</button>
                                    </div>
                                )}

                                {!['age', 'bmi', 'tasbih', 'qr', 'pwd'].includes(activeTool) && (
                                    <div className="text-center py-6">
                                        <p className="text-xs text-gray-500">Coming soon in next update! 🚀</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            );
        };

        // --- 4. UPCOMING TAB ---
        const UpcomingPage = ({ items }) => (
            <div className="min-h-screen p-4 pb-20">
                <h1 className="text-lg font-bold text-gray-800 mb-4">📅 Upcoming Releases</h1>
                {items.length === 0 && <p className="text-center text-gray-400 mt-12 text-xs">No upcoming items announced yet.</p>}
                <div className="space-y-3">
                    {items.map((it, i) => (
                        <div key={i} className="bg-white p-3.5 rounded-2xl border border-gray-100 flex gap-3 shadow-sm">
                            <img src={it.thumb} className="w-20 h-24 object-cover rounded-xl" />
                            <div>
                                <h3 className="font-bold text-xs text-gray-800">{it.title}</h3>
                                <p className="text-[10px] text-gray-400 mt-1">Release: {it.release_date || "Coming Soon"}</p>
                                <span className="inline-block mt-2 text-[9px] bg-red-100 text-red-600 font-extrabold px-2 py-0.5 rounded-full">Coming Soon</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );

        // --- 5. SETTINGS / PROFILE TAB ---
        const SettingPage = () => {
            const [redeemCode, setRedeemCode] = useState('');
            const [msg, setMsg] = useState('');

            const applyCode = () => {
                if(!redeemCode.trim()) return;
                fetch(`/api/redeem?code=${encodeURIComponent(redeemCode)}`)
                    .then(r => r.json())
                    .then(res => {
                        setMsg(res.msg);
                        setRedeemCode('');
                    });
            };

            return (
                <div className="min-h-screen p-4 pb-20">
                    <h1 className="text-lg font-bold text-gray-800 mb-4">⚙️ App Settings</h1>
                    <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm mb-4">
                        <h3 className="font-bold text-xs text-gray-700 mb-2">🎁 Redeem Premium Membership</h3>
                        <div className="flex gap-2">
                            <input 
                                type="text"
                                placeholder="Enter 8-digit Code"
                                value={redeemCode}
                                onChange={e=>setRedeemCode(e.target.value)}
                                className="flex-1 bg-gray-50 border border-gray-200 text-xs px-3 py-2 rounded-xl uppercase"
                            />
                            <button onClick={applyCode} className="bg-emerald-500 text-white font-bold text-xs px-4 rounded-xl">Apply</button>
                        </div>
                        {msg && <p className="text-[11px] font-bold text-indigo-600 mt-2">{msg}</p>}
                    </div>
                </div>
            );
        };

        // --- ROOT COMPONENT ---
        const App = () => {
            const [tab, setTab] = useState('home');
            const [data, setData] = useState({ items: [], sliders: [], upcoming: [], botname: '', promo: '' });
            const [selectedItem, setSelectedItem] = useState(null);
            const [favorites, setFavorites] = useState([]);
            const [searchQuery, setSearchQuery] = useState('');

            useEffect(() => {
                if (window.Telegram?.WebApp) {
                    window.Telegram.WebApp.expand();
                }
                fetch('/api/data').then(r => r.json()).then(d => setData(d));
            }, []);

            const toggleFav = (item) => {
                if (favorites.some(f => f.title === item.title)) {
                    setFavorites(favorites.filter(f => f.title !== item.title));
                } else {
                    setFavorites([...favorites, item]);
                }
            };

            return (
                <div>
                    {selectedItem ? (
                        <DetailsPage 
                            item={selectedItem} 
                            goBack={() => setSelectedItem(null)} 
                            zoonid={data.zoonid} 
                            onToggleFav={toggleFav}
                            isFav={favorites.some(f => f.title === selectedItem.title)}
                        />
                    ) : (
                        <div>
                            {tab === 'home' && <HomePage data={data} onSelect={setSelectedItem} onSearch={setSearchQuery} searchQuery={searchQuery} />}
                            {tab === 'favorite' && <UpcomingPage items={favorites} />}
                            {tab === 'tools' && <ToolsPage />}
                            {tab === 'upcoming' && <UpcomingPage items={data.upcoming || []} />}
                            {tab === 'setting' && <SettingPage />}
                        </div>
                    )}

                    {/* Bottom Navigation */}
                    <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur border-t border-gray-100 flex justify-around py-2.5 z-40 text-[10px] font-bold text-gray-500 shadow-lg">
                        <button onClick={()=>{setSelectedItem(null); setTab('home');}} className={`flex flex-col items-center ${tab==='home'&&!selectedItem?'text-red-500':''}`}>
                            <span className="text-xl">🏠</span> Home
                        </button>
                        <button onClick={()=>{setSelectedItem(null); setTab('favorite');}} className={`flex flex-col items-center ${tab==='favorite'?'text-red-500':''}`}>
                            <span className="text-xl">❤️</span> Favorite
                        </button>
                        <button onClick={()=>{setSelectedItem(null); setTab('tools');}} className={`flex flex-col items-center ${tab==='tools'?'text-red-500':''}`}>
                            <span className="text-xl">🛠</span> Tools
                        </button>
                        <button onClick={()=>{setSelectedItem(null); setTab('upcoming');}} className={`flex flex-col items-center ${tab==='upcoming'?'text-red-500':''}`}>
                            <span className="text-xl">📅</span> Upcoming
                        </button>
                        <button onClick={()=>{setSelectedItem(null); setTab('setting');}} className={`flex flex-col items-center ${tab==='setting'?'text-red-500':''}`}>
                            <span className="text-xl">⚙️</span> Setting
                        </button>
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

# ==========================================
# 🌐 ৩. ওয়েব সার্ভার ব্যাকএন্ড API
# ==========================================
async def handle_webapp(request):
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_api_data(request):
    movies = await db.movies.find().sort('_id', -1).to_list(100)
    series = await db.series.find().sort('_id', -1).to_list(100)
    upcoming = await db.upcoming.find().sort('_id', -1).to_list(20)
    all_items = movies + series
    for it in all_items: it['_id'] = str(it['_id'])
    for u in upcoming: u['_id'] = str(u['_id'])
    
    settings = await db.settings.find().to_list(100)
    data = {"items": all_items, "sliders": [], "upcoming": upcoming, "zoonid": "", "botname": "Moviee", "promo": ""}
    for s in settings:
        if s.get('type') == 'sliders': data['sliders'] = s.get('list', [])
        elif s.get('type') == 'zoonid': data['zoonid'] = s.get('id', '')
        elif s.get('type') == 'botname': data['botname'] = s.get('name', 'Moviee')
        elif s.get('type') == 'promo': data['promo'] = s.get('text', '')
    
    return web.json_response(data)

async def handle_redeem(request):
    code = request.query.get('code', '').strip().upper()
    doc = await db.redeems.find_one({"code": code, "used": False})
    if doc:
        await db.redeems.update_one({"_id": doc['_id']}, {"$set": {"used": True}})
        return web.json_response({"success": True, "msg": f"✅ Successful! {doc['dur']} Premium Unlocked!"})
    return web.json_response({"success": False, "msg": "❌ Invalid or already used code!"})

# ==========================================
# 🤖 ৪. FSM স্টেটস
# ==========================================
class MovieState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    thumb = State(); q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class SeriesState(StatesGroup):
    title = State(); year = State(); category = State(); language = State()
    thumb = State(); s_num = State(); e_num = State(); q_res = State(); q_link = State(); q_size = State(); ask_more = State()

class UpcomingState(StatesGroup):
    title = State(); date = State(); thumb = State()

class BroadcastState(StatesGroup):
    msg = State()

# ==========================================
# 🚀 ৫. টেলিগ্রাম বট হ্যান্ডলার ও কমান্ডস
# ==========================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # সেভ ইউজার ডাটা
    await db.users.update_one(
        {"uid": message.from_user.id}, 
        {"$set": {"name": message.from_user.full_name, "username": message.from_user.username}},
        upsert=True
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍿 WATCH NOW", web_app=WebAppInfo(url=WEB_APP_URL))],
        [
            InlineKeyboardButton(text="🎁 Share Friend", switch_inline_query="Check this awesome movie bot!"),
            InlineKeyboardButton(text="📡 Join Channel", url="https://t.me/Movieelinkbo")
        ]
    ])
    
    welcome_text = (
        f"👋 হ্যালো **{message.from_user.full_name}**!\n\n"
        "🎬 এখানে পাবেন নিত্য নতুন মুভি, ড্রামা ও ওয়েব সিরিজ কালেকশন — দেরি না করে নিচের **WATCH NOW** বাটনে ক্লিক করুন!"
    )
    await message.answer(welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- 🎬 ADD MOVIE FLOW ---
@dp.message(Command("movies"))
async def add_movie_cmd(message: types.Message, command: CommandObject, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.clear()
    if command.args:
        args = command.args.rsplit(' ', 1)
        await state.update_data(title=args[0], year=args[1] if len(args) > 1 else "2026", qualities=[])
        await prompt_movie_cat(message, state)
    else:
        await message.answer("🎬 মুভির নাম লিখুন:")
        await state.set_state(MovieState.title)

@dp.message(MovieState.title)
async def m_year(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text, qualities=[])
    await message.answer("📅 সাল দিন (উদাঃ 2026):")
    await state.set_state(MovieState.year)

@dp.message(MovieState.year)
async def m_year_save(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await prompt_movie_cat(message, state)

async def prompt_movie_cat(message, state):
    cats = ["Action", "Drama", "Natok", "Romance", "Comedy", "Thriller"]
    kb = [[InlineKeyboardButton(text=c, callback_data=f"mc_{c}")] for c in cats]
    await message.answer("📁 ক্যাটাগরি বেছে নিন:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(MovieState.category)

@dp.callback_query(MovieState.category)
async def m_cat_cb(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data.replace("mc_", ""))
    langs = ["Bangla", "Hindi", "English", "Tamil"]
    kb = [[InlineKeyboardButton(text=l, callback_data=f"ml_{l}")] for l in langs]
    await call.message.edit_text("🗣 ভাষা নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await state.set_state(MovieState.language)

@dp.callback_query(MovieState.language)
async def m_lang_cb(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(language=call.data.replace("ml_", ""))
    await call.message.edit_text("🖼 এবার মুভির পোস্টার ছবি পাঠান অথবা ছবির ডাইরেক্ট লিঙ্ক দিন:")
    await state.set_state(MovieState.thumb)

@dp.message(MovieState.thumb)
async def m_thumb_get(message: types.Message, state: FSMContext):
    thumb = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{(await bot.get_file(message.photo[-1].file_id)).file_path}" if message.photo else message.text
    await state.update_data(thumb=thumb)
    await message.answer("📺 কোয়ালিটি দিন (উদাঃ 720p, 1080p):")
    await state.set_state(MovieState.q_res)

@dp.message(MovieState.q_res)
async def m_res_get(message: types.Message, state: FSMContext):
    await state.update_data(cur_res=message.text)
    await message.answer("🔗 ডাউনলোড লিংক দিন:")
    await state.set_state(MovieState.q_link)

@dp.message(MovieState.q_link)
async def m_link_get(message: types.Message, state: FSMContext):
    await state.update_data(cur_link=message.text)
    await message.answer("💾 ফাইলের সাইজ দিন (উদাঃ 1.2 GB):")
    await state.set_state(MovieState.q_size)

@dp.message(MovieState.q_size)
async def m_size_get(message: types.Message, state: FSMContext):
    d = await state.get_data()
    q = d.get('qualities', [])
    q.append({"res": d['cur_res'], "link": d['cur_link'], "size": message.text})
    await state.update_data(qualities=q)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ আরও কোয়ালিটি যোগ করুন", callback_data="m_more")],
        [InlineKeyboardButton(text="✅ আপলোড শেষ করুন", callback_data="m_done")]
    ])
    await message.answer(f"✅ {len(q)} টি কোয়ালিটি যোগ হয়েছে।", reply_markup=markup)
    await state.set_state(MovieState.ask_more)

@dp.callback_query(MovieState.ask_more)
async def m_finish(call: types.CallbackQuery, state: FSMContext):
    if call.data == "m_more":
        await call.message.edit_text("📺 পরবর্তী কোয়ালিটি লিখুন:")
        await state.set_state(MovieState.q_res)
    else:
        d = await state.get_data()
        await db.movies.insert_one({
            "type": "movie", "title": d['title'], "year": d['year'], 
            "category": d['category'], "language": d['language'], 
            "thumb": d['thumb'], "qualities": d['qualities'], "likes": 0, "downloads": 0
        })
        await call.message.edit_text(f"🎉 **{d['title']}** সফলভাবে ওয়েবসাইটে যুক্ত হয়েছে!")
        await state.clear()

# --- 📅 UPCOMING MOVIE COMMAND ---
@dp.message(Command("addupcoming"))
async def add_upc_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.clear()
    await message.answer("🎬 আপকামিং নাটক/মুভির নাম লিখুন:")
    await state.set_state(UpcomingState.title)

@dp.message(UpcomingState.title)
async def upc_date(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📅 সম্ভাব্য রিলিজ ডেট দিন (উদাঃ 15 Dec 2026):")
    await state.set_state(UpcomingState.date)

@dp.message(UpcomingState.date)
async def upc_thumb(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("🖼 পোস্টার ছবি অথবা লিঙ্ক পাঠান:")
    await state.set_state(UpcomingState.thumb)

@dp.message(UpcomingState.thumb)
async def upc_save(message: types.Message, state: FSMContext):
    thumb = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{(await bot.get_file(message.photo[-1].file_id)).file_path}" if message.photo else message.text
    d = await state.get_data()
    await db.upcoming.insert_one({"title": d['title'], "release_date": d['date'], "thumb": thumb})
    await message.answer("✅ আপকামিং তালিকায় যুক্ত হয়েছে!")
    await state.clear()

# --- 🖼️ স্লাইডার ও ব্যানার কমান্ডস ---
@dp.message(Command("addslider"))
async def add_sld(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    if not command.args: return await message.answer("⚠️ ইমেজ URL দিন: `/addslider https://img.jpg`", parse_mode="Markdown")
    await db.settings.update_one({"type": "sliders"}, {"$push": {"list": command.args}}, upsert=True)
    await message.answer("✅ নতুন স্লাইডার ছবি যোগ করা হয়েছে!")

@dp.message(Command("deleteslider"))
async def del_sld(message: types.Message):
    if not is_admin(message.from_user.id): return
    await db.settings.delete_one({"type": "sliders"})
    await message.answer("✅ সব স্লাইডার মুছে ফেলা হয়েছে।")

# --- 📢 ব্রডকাস্ট মেসেজ পাঠানো ---
@dp.message(Command("broadcast"))
async def broad_cmd(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await message.answer("📢 সব ইউজারকে পাঠানোর জন্য মেসেজটি লিখুন:")
    await state.set_state(BroadcastState.msg)

@dp.message(BroadcastState.msg)
async def broad_send(message: types.Message, state: FSMContext):
    users = await db.users.find().to_list(10000)
    count = 0
    for u in users:
        try:
            await bot.send_message(u['uid'], message.text)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"✅ {count} জন ইউজারের কাছে মেসেজ পৌঁছেছে!")
    await state.clear()

# --- 🎟️ রিডিম কোড তৈরি ---
@dp.message(Command("addredeem"))
async def add_rd(message: types.Message, command: CommandObject):
    if not is_admin(message.from_user.id): return
    args = (command.args or "1month 5").split()
    dur = args[0]
    count = int(args[1]) if len(args) > 1 else 1
    codes = [''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) for _ in range(count)]
    await db.redeems.insert_many([{"code": c, "dur": dur, "used": False} for c in codes])
    await message.answer(f"✅ {count} টি রিডিম কোড তৈরি হয়েছে ({dur}):\n\n`" + "`\n`".join(codes) + "`", parse_mode="Markdown")

# ==========================================
# 🚀 ৬. Render সার্ভার রানার (Bug Fixed)
# ==========================================
async def main():
    logging.basicConfig(level=logging.INFO)
    
    # একাধিক ইনস্ট্যান্স রোধ ও পেন্ডিং আপডেট ড্রপ
    await bot.delete_webhook(drop_pending_updates=True)

    # aiohttp ওয়েব সার্ভার সেটআপ
    app = web.Application()
    app.router.add_get('/', handle_webapp)
    app.router.add_get('/api/data', handle_api_data)
    app.router.add_get('/api/redeem', handle_redeem)

    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    # ❗️ সমাধান: site.start() দেওয়া হলো যাতে Render পোর্ট স্ক্যানিং সফল হয়
    await site.start()
    print(f"✅ Server running and listening on port: {port}")

    # ডিসপ্যাচার পোলিং শুরু
    print("🤖 Bot polling started successfully...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
