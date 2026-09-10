import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.future import select

from app.db.models import EducationalLesson, EducationalModule
from app.db.session import async_session_maker


async def seed_education():
    async with async_session_maker() as db:
        # We'll just delete existing and recreate to keep it simple and clean.
        # But `UserLessonProgress` depends on it, so we can't easily truncate.
        # Instead, we will add new ones if module count is < 3.
        res = await db.execute(select(EducationalModule))
        existing_modules = res.scalars().all()
        if len(existing_modules) >= 4:
            print("Already seeded.")
            return

        m_tech = EducationalModule(
            slug="technical-analysis", title="Teknik Analiz",
            description="Grafik okuma ve teknik göstergeler.", category="TECHNICAL_ANALYSIS", display_order=1
        )
        m_form = EducationalModule(
            slug="formations", title="Formasyonlar",
            description="Grafik formasyonları ve anlamları.", category="TECHNICAL_ANALYSIS", display_order=2
        )
        m_fund = EducationalModule(
            slug="fundamentals", title="Temel Analiz",
            description="Şirket değerleme metrikleri.", category="FUNDAMENTALS", display_order=3
        )
        m_port = EducationalModule(
            slug="portfolio-risk", title="Portföy ve Risk",
            description="Risk yönetimi ve portföy çeşitlendirmesi.", category="PORTFOLIO", display_order=4
        )
        db.add_all([m_tech, m_form, m_fund, m_port])
        await db.commit()
        await db.refresh(m_tech)
        await db.refresh(m_form)
        await db.refresh(m_fund)
        await db.refresh(m_port)

        lessons = [
            # Technical Analysis
            EducationalLesson(
                module_id=m_tech.id, slug="mum-grafik-nedir", title="Mum Grafik Nedir?",
                summary="Fiyat hareketlerini görselleştirmenin temel yolu.",
                content_beginner="Mum grafikler, belirli bir zaman dilimindeki açılış, kapanış, en yüksek ve en düşük fiyatları gösterir. Yeşil mumlar yükselişi, kırmızı mumlar düşüşü ifade eder.",
                content_detailed="Japon mum grafikleri (Candlestick), fiyatın belirli bir periyottaki hareket alanını (Range) özetler. Mum gövdesi (Body) açılış-kapanış arasını, fitiller (Wick/Shadow) ise en yüksek ve en düşük fiyatları gösterir. Tek başına yön tahmini yapmak yerine destek ve direnç noktalarında teyit amaçlı kullanılırlar.",
                display_order=1, estimated_minutes=3
            ),
            EducationalLesson(
                module_id=m_tech.id, slug="trend-nedir", title="Trend Nedir?",
                summary="Piyasanın genel yön eğilimi.",
                content_beginner="Trend, fiyatların genel olarak hangi yöne gittiğini gösterir. Yükselen trendde fiyatlar sürekli daha yüksek tepeler yapar, düşen trendde ise sürekli daha düşük dipler yapar.",
                content_detailed="Teknik analizin temel varsayımı 'fiyatlar trendler halinde hareket eder' şeklindedir. Bir yükseliş trendi (Uptrend) higher-highs ve higher-lows ile, düşüş trendi (Downtrend) lower-highs ve lower-lows ile tanımlanır. Trende karşı işlem yapmak (Counter-trend trading) yüksek risk içerir.",
                display_order=2, estimated_minutes=4
            ),
            EducationalLesson(
                module_id=m_tech.id, slug="destek-direnc", title="Destek ve Direnç",
                summary="Fiyatın dönme eğiliminde olduğu kritik seviyeler.",
                content_beginner="Destek fiyatın düşmesini engelleyen, Direnç ise fiyatın yükselmesini engelleyen hayali seviyelerdir. Fiyat bu seviyelere geldiğinde yön değiştirebilir veya kırarak hareketini hızlandırabilir.",
                content_detailed="Destek (Support) alıcıların yoğunlaştığı fiyat seviyesidir. Direnç (Resistance) ise satıcıların yoğunlaştığı seviyedir. Bu seviyeler kırıldığında roller değişir (Polarity prensibi): Kırılan direnç destek olur, kırılan destek direnç olur. Bu seviyeler kesin çizgiler değil, 'bölgeler' olarak değerlendirilmelidir.",
                display_order=3, estimated_minutes=4
            ),
            EducationalLesson(
                module_id=m_tech.id, slug="rsi-nedir", title="RSI",
                summary="Aşırı alım ve aşırı satım bölgelerini gösteren momentum osilatörü.",
                content_beginner="RSI, bir hissenin çok hızlı yükseldiğini veya düştüğünü gösterir. 30'un altı hissenin çok satıldığını (aşırı satım), 70'in üstü ise çok alındığını (aşırı alım) işaret eder.",
                content_detailed="RSI (Relative Strength Index), 0-100 arasında değer alır. RSI tek başına bir AL/SAT sinyali DEĞİLDİR. Sadece güçlü bir trend olup olmadığını gösterir. Uyuşmazlıklar (Divergence) fiyat ile RSI uyumsuz olduğunda trend dönüşünün sinyali olabilir.",
                display_order=4, estimated_minutes=3
            ),
            EducationalLesson(
                module_id=m_tech.id, slug="macd-nedir", title="MACD",
                summary="Trend izleyen momentum indikatörü.",
                content_beginner="MACD, iki hareketli ortalamanın birbirine yaklaşmasını ve uzaklaşmasını analiz eder. Histogram ve sinyal çizgisi kesişmeleriyle potansiyel dönüşleri gösterir.",
                content_detailed="Moving Average Convergence Divergence (MACD) genellikle 12 ve 26 günlük EMA farkından oluşur. Sinyal çizgisi (Signal Line) MACD hattını yukarı keserse Bullish, aşağı keserse Bearish sinyal kabul edilir.",
                display_order=5, estimated_minutes=4
            ),
            EducationalLesson(
                module_id=m_tech.id, slug="bollinger-bantlari", title="Bollinger Bantları",
                summary="Fiyat volatilitesini ölçen bantlar.",
                content_beginner="Bollinger Bantları, fiyatın standart sapmasına göre çizilir. Fiyat üst banta yaklaştığında hisse nispeten pahalı, alt banta yaklaştığında ise nispeten ucuz olarak yorumlanabilir.",
                content_detailed="John Bollinger tarafından geliştirilen bantlar, genellikle 20 günlük SMA ve ±2 standart sapma kullanır. Bantların daralması (Squeeze) yakında sert bir fiyat hareketi olabileceğine (volatilite patlamasına) işaret eder.",
                display_order=6, estimated_minutes=4
            ),
            EducationalLesson(
                module_id=m_tech.id, slug="sma-ema-nedir", title="SMA ve EMA",
                summary="Fiyat hareketlerini yumuşatan hareketli ortalamalar.",
                content_beginner="Hareketli ortalamalar fiyat dalgalanmalarını filtreler ve trendi daha net görmenizi sağlar. Kısa ortalama uzun ortalamayı yukarı keserse yükseliş sinyali olabilir.",
                content_detailed="Basit Hareketli Ortalama (SMA) her güne eşit ağırlık verirken, Üstel Hareketli Ortalama (EMA) son günlere daha fazla ağırlık verir, bu yüzden fiyat değişimlerine daha hızlı tepki verir.",
                display_order=7, estimated_minutes=5
            ),
            # Formations
            EducationalLesson(
                module_id=m_form.id, slug="cift-tepe-cift-dip", title="Çift Tepe / Çift Dip",
                summary="Güçlü trend dönüş formasyonları.",
                content_beginner="Fiyatın aynı seviyeden iki kez dönmesidir. Çift tepe yükselişin bittiğini, çift dip düşüşün bittiğini işaret edebilir.",
                content_detailed="Formasyonun tamamlanması için tepe/dip noktaları arasındaki boyun çizgisinin (Neckline) kırılması gerekir. Kırılmadan önce formasyon sadece bir ihtimaldir. İşlem hacmi kırılımı teyit etmelidir.",
                display_order=1, estimated_minutes=3
            ),
            EducationalLesson(
                module_id=m_form.id, slug="obo-tobo", title="OBO / TOBO",
                summary="Omuz Baş Omuz trend dönüş formasyonu.",
                content_beginner="OBO yükseliş trendinin sonunu, TOBO ise düşüş trendinin sonunu gösteren en güvenilir formasyonlardan biridir.",
                content_detailed="Üç tepeden oluşur; ortadaki tepe (Baş) en yüksektir. Boyun çizgisi (Neckline) kırıldığında formasyon çalışmaya başlar. Formasyon hedefi genellikle Baş ile boyun çizgisi arasındaki mesafe kadardır.",
                display_order=2, estimated_minutes=4
            ),
            # Fundamental
            EducationalLesson(
                module_id=m_fund.id, slug="fk-nedir", title="F/K",
                summary="Fiyat/Kazanç Oranı.",
                content_beginner="F/K oranı, yatırdığınız paranın şirketin kârıyla kaç yılda size döneceğini gösterir. Düşük F/K hissenin ucuz olduğunu düşündürebilir.",
                content_detailed="Piyasanın şirket kârına ne kadar değer biçtiğini gösterir. Aynı sektördeki şirketleri karşılaştırmak için kullanılır. Eksi F/K şirketin zarar ettiğini gösterir.",
                display_order=1, estimated_minutes=3
            ),
            EducationalLesson(
                module_id=m_fund.id, slug="kap-nedir", title="KAP Nedir?",
                summary="Kamuyu Aydınlatma Platformu.",
                content_beginner="Borsada işlem gören şirketlerin yatırımcıları bilgilendirmek için resmi duyuru yaptıkları platformdur.",
                content_detailed="KAP bildirimleri (yeni iş ilişkisi, kâr payı, sermaye artırımı vb.) hisse fiyatını doğrudan etkileyebilir. İçsel bilgiye erişim eşitliği için kritik bir sistemdir.",
                display_order=2, estimated_minutes=2
            ),
            # Portfolio / Risk
            EducationalLesson(
                module_id=m_port.id, slug="cesitlendirme", title="Çeşitlendirme",
                summary="Tüm yumurtaları aynı sepete koymamak.",
                content_beginner="Portföyünüzü farklı sektörlerdeki hisselere veya varlık sınıflarına bölmektir. Bir şirket kötü gitse bile diğerleri portföyü dengeler.",
                content_detailed="Modern Portföy Teorisine göre çeşitlendirme, beklenen getiriyi düşürmeden sistematik olmayan (şirkete özgü) riski minimize eder. 10-15 arası farklı sektör hissesi genel kabul gören bir çeşitlendirmedir.",
                display_order=1, estimated_minutes=4
            ),
            EducationalLesson(
                module_id=m_port.id, slug="stop-loss", title="Stop-Loss",
                summary="Zararı kesme seviyesi.",
                content_beginner="İşleme girmeden önce zararı kabulleneceğiniz noktayı belirlemek. Hisse o fiyata düştüğünde duygusuzca satmalısınız.",
                content_detailed="Sermayeyi korumanın en önemli kuralıdır. Psikolojik hataları (düştükçe bekleme) önler. Teknik bir seviyenin (örn: önemli bir destek) biraz altına konulmalıdır.",
                display_order=2, estimated_minutes=3
            ),
        ]
        db.add_all(lessons)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed_education())
