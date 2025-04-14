import tweepy
import time
import logging
import os
import argparse
from dotenv import load_dotenv

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autoreply.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Muat kredensial dari file .env
load_dotenv()

# Kredensial API Twitter
API_KEY = os.getenv('TWITTER_API_KEY')
API_SECRET = os.getenv('TWITTER_API_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

def authenticate_twitter():
    """Autentikasi ke Twitter API."""
    try:
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        api.verify_credentials()
        logger.info("Autentikasi berhasil")
        return api
    except tweepy.TweepError as e:
        logger.error(f"Gagal autentikasi: {e}")
        raise

def read_replies(file_path):
    """Baca balasan dari file teks."""
    try:
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} tidak ditemukan")
            raise FileNotFoundError(f"File {file_path} tidak ditemukan")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            replies = [line.strip() for line in file if line.strip()]
        
        if not replies:
            logger.error("File balasan kosong")
            raise ValueError("File balasan kosong")
        
        logger.info(f"Berhasil membaca {len(replies)} balasan dari {file_path}")
        return replies
    except Exception as e:
        logger.error(f"Gagal membaca file: {e}")
        raise

def send_tweet(api, text, tweet_id=None):
    """Kirim tweet atau balasan."""
    if len(text) > 280:
        logger.error(f"Teks terlalu panjang ({len(text)} karakter): {text}")
        return
    
    try:
        if tweet_id:
            api.update_status(status=text, in_reply_to_status_id=tweet_id)
            logger.info(f"Balasan terkirim ke tweet {tweet_id}: {text}")
        else:
            api.update_status(status=text)
            logger.info(f"Tweet terkirim: {text}")
    except tweepy.TweepError as e:
        logger.error(f"Gagal mengirim tweet: {e}")

def main():
    """Fungsi utama."""
    # Parse argumen command line
    parser = argparse.ArgumentParser(description='Twitter Auto Reply Bot')
    parser.add_argument('--file', default='replies.txt', help='File berisi balasan')
    parser.add_argument('--interval', type=int, default=600, help='Interval dalam detik antar tweet')
    parser.add_argument('--tweet-id', default='', help='ID tweet yang akan dibalas')
    args = parser.parse_args()
    
    REPLIES_FILE = args.file
    INTERVAL = args.interval
    TWEET_ID = args.tweet_id if args.tweet_id else None
    
    try:
        # Autentikasi
        api = authenticate_twitter()
        
        # Baca balasan
        replies = read_replies(REPLIES_FILE)
        
        # Kirim balasan
        for i, reply in enumerate(replies, 1):
            logger.info(f"Mengirim balasan ke-{i} dari {len(replies)}")
            send_tweet(api, reply, TWEET_ID)
            if i < len(replies):  # Jeda kecuali untuk balasan terakhir
                logger.info(f"Menunggu {INTERVAL} detik...")
                time.sleep(INTERVAL)
        
        logger.info("Selesai mengirim semua balasan")
    
    except KeyboardInterrupt:
        logger.info("Program dihentikan oleh pengguna")
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
