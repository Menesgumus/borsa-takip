import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import async_session_maker
from app.db.models import EducationalModule, EducationalLesson

async def seed_education():
    async with async_session_maker() as db:
        # Check if already seeded
        res = await db.execute(select(EducationalModule).limit(1))
        if res.scalars().first():
            print("Already seeded.")
            return

        m_tech = EducationalModule(
            slug="technical-analysis", title="Teknik Analiz Temelleri",
            description="Fiyat grafiklerini okumayı öğrenin.", category="TECHNICAL_ANALYSIS", display_order=1
        )
        m_fund = EducationalModule(
            slug="fundamentals", title="Temel Analiz",
            description="Şirket değerleme metrikleri.", category="FUNDAMENTALS", display_order=2
        )
        db.add_all([m_tech, m_fund])
        await db.commit()
        await db.refresh(m_tech)
        await db.refresh(m_fund)

        l_rsi = EducationalLesson(
            module_id=m_tech.id, slug="rsi-nedir", title="RSI (Relative Strength Index)",
            summary="Aşırı alım ve aşırı satım bölgelerini gösteren momentum indikatörü.",
            content_beginner="RSI, bir hissenin çok hızlı yükseldiğini veya düştüğünü gösterir. 30'un altı hissenin çok satıldığını (ucuzlamış olabileceğini), 70'in üstü ise çok alındığını (pahalanmış olabileceğini) işaret eder.",
            content_detailed="RSI (Göreceli Güç Endeksi), J. Welles Wilder tarafından geliştirilen, fiyat hareketlerinin hızını ve değişimini ölçen bir momentum osilatörüdür. 0-100 arasında değer alır. RSI > 70 Aşırı Alım (Overbought), RSI < 30 Aşırı Satım (Oversold) olarak kabul edilir. Ancak güçlü trendlerde RSI uzun süre bu bölgelerde kalabilir (False Signal). Deterministik motorumuzda RSI tek başına değil, MACD ve Trend ile birlikte değerlendirilir.",
            key_points="Momentum,Aşırı Alım,Aşırı Satım,False Signal", related_terms="MACD,Momentum",
            display_order=1, estimated_minutes=3
        )
        
        l_macd = EducationalLesson(
            module_id=m_tech.id, slug="macd-nedir", title="MACD İndikatörü",
            summary="Trend dönüşlerini yakalamak için kullanılan osilatör.",
            content_beginner="MACD, kısa vadeli trendin uzun vadeli trende kıyasla ne yöne gittiğini gösterir. Çizgiler yukarı kesiştiğinde AL, aşağı kesiştiğinde SAT sinyali üretebilir.",
            content_detailed="Moving Average Convergence Divergence (MACD), trend izleyen bir momentum indikatörüdür. Genellikle 12 ve 26 günlük Üstel Hareketli Ortalamaların (EMA) farkından oluşur. Sinyal çizgisi (Signal Line) MACD hattını yukarı keserse Bullish, aşağı keserse Bearish sinyal kabul edilir.",
            key_points="Trend,Kesişim,EMA", related_terms="EMA,RSI",
            display_order=2, estimated_minutes=4
        )

        l_fk = EducationalLesson(
            module_id=m_fund.id, slug="fk-nedir", title="Fiyat/Kazanç (F/K) Oranı",
            summary="Şirketin ne kadar sürede kendi fiyatını amorti ettiğini gösterir.",
            content_beginner="F/K oranı, bir hisseye yatırdığınız paranın, şirketin mevcut kârlılığıyla kaç yılda geri döneceğini gösterir. Düşük F/K hissenin ucuz, yüksek F/K pahalı olduğunu gösterebilir.",
            content_detailed="Fiyat/Kazanç (P/E) oranı, hisse fiyatının hisse başına kâra bölünmesiyle bulunur. Ortalama F/K sektöre göre değişir. F/K < 15 genelde makul değerleme sayılırken, F/K > 30 aşırı fiyatlanma veya yüksek büyüme beklentisi olarak yorumlanır. Eksi F/K, şirketin zarar ettiğini gösterir ve Karar Motorumuz tarafından riskli (NULL/Warning) kabul edilir.",
            key_points="Değerleme,Kârlılık,Amortisman", related_terms="PD/DD",
            display_order=1, estimated_minutes=5
        )

        db.add_all([l_rsi, l_macd, l_fk])
        await db.commit()
        print("Education seed complete.")

if __name__ == "__main__":
    asyncio.run(seed_education())
