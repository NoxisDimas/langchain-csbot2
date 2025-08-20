#!/usr/bin/env python3
"""
Setup script untuk inisialisasi RAG database dengan sample data
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def setup_sample_data():
    """Setup sample data untuk RAG system"""
    print("🚀 Setting up RAG database with sample data...")
    
    try:
        from app.services.document_service import DocumentService
        from app.services.vectorstore_service import VectorStoreService
        from app.config import get_settings
        
        settings = get_settings()
        ds = DocumentService()
        vs = VectorStoreService()
        
        # Sample data untuk testing
        sample_documents = [
            {
                "filename": "loyalty_program.txt",
                "content": """
                Program Loyalitas dan Diskon

                Program Loyalitas:
                - Poin Rewards: Setiap pembelian Rp 10.000 = 1 poin
                - Silver Member: 100-500 poin (diskon 5%)
                - Gold Member: 501-1000 poin (diskon 10%)
                - Platinum Member: 1001+ poin (diskon 15%)

                Diskon Khusus:
                - Diskon Member Baru: 10% untuk pembelian pertama
                - Diskon Hari Spesial: 20% di hari ulang tahun member
                - Diskon Bulk Purchase: 15% untuk pembelian di atas Rp 500.000
                - Diskon Referral: 5% untuk setiap teman yang mendaftar

                Cara Mendapatkan Poin:
                1. Belanja produk apapun
                2. Review produk (10 poin per review)
                3. Share di social media (5 poin per share)
                4. Referral teman (50 poin per referral)

                Penukaran Poin:
                - 100 poin = voucher Rp 10.000
                - 500 poin = voucher Rp 50.000
                - 1000 poin = voucher Rp 100.000
                """
            },
            {
                "filename": "payment_methods.txt", 
                "content": """
                Metode Pembayaran yang Tersedia

                Transfer Bank:
                - BCA: 1234567890 (a.n. Toko Online)
                - BNI: 0987654321 (a.n. Toko Online)
                - Mandiri: 1122334455 (a.n. Toko Online)

                E-Wallet:
                - OVO: Terintegrasi otomatis
                - GoPay: Terintegrasi otomatis
                - Dana: Terintegrasi otomatis
                - ShopeePay: Terintegrasi otomatis

                Kartu Kredit/Debit:
                - Visa
                - Mastercard
                - JCB

                COD (Cash on Delivery):
                - Tersedia untuk area tertentu
                - Biaya tambahan Rp 5.000
                - Maksimal pembayaran Rp 500.000

                Proses Pembayaran:
                1. Pilih metode pembayaran
                2. Upload bukti transfer (jika transfer bank)
                3. Konfirmasi pembayaran
                4. Pesanan diproses dalam 1-2 jam
                """
            },
            {
                "filename": "shipping_info.txt",
                "content": """
                Informasi Pengiriman

                Estimasi Waktu Pengiriman:
                - Jakarta: 1-2 hari kerja
                - Jawa Barat: 2-3 hari kerja
                - Jawa Tengah: 2-3 hari kerja
                - Jawa Timur: 3-4 hari kerja
                - Sumatra: 4-7 hari kerja
                - Kalimantan: 5-8 hari kerja
                - Sulawesi: 6-9 hari kerja
                - Papua: 7-10 hari kerja

                Partner Logistik:
                - JNE: Regular, YES, OKE
                - SiCepat: Regular, HALU
                - J&T Express: Regular, EZ
                - Ninja Express: Regular, Same Day
                - GoSend: Instant delivery

                Biaya Pengiriman:
                - Jakarta: Rp 8.000 - Rp 15.000
                - Jawa: Rp 12.000 - Rp 25.000
                - Sumatra: Rp 25.000 - Rp 35.000
                - Kalimantan: Rp 30.000 - Rp 45.000
                - Sulawesi: Rp 35.000 - Rp 50.000
                - Papua: Rp 50.000 - Rp 75.000

                Gratis Ongkir:
                - Pembelian minimal Rp 100.000
                - Member Gold dan Platinum
                - Promo khusus hari tertentu
                """
            },
            {
                "filename": "return_policy.txt",
                "content": """
                Kebijakan Pengembalian dan Refund

                Syarat Pengembalian:
                - Barang dalam kondisi utuh dan lengkap
                - Tagihan dan kemasan asli
                - Maksimal 7 hari setelah diterima
                - Foto bukti kerusakan (jika ada)

                Alasan Pengembalian yang Diterima:
                - Barang rusak saat pengiriman
                - Barang tidak sesuai pesanan
                - Barang cacat produksi
                - Ukuran tidak sesuai
                - Warna tidak sesuai

                Proses Pengembalian:
                1. Hubungi customer service
                2. Kirim foto bukti
                3. CS akan memberikan label retur
                4. Kirim barang ke warehouse
                5. Refund diproses dalam 3-5 hari kerja

                Kebijakan Refund:
                - Refund penuh untuk barang rusak
                - Refund 90% untuk pengembalian (potong ongkir)
                - Voucher untuk pembelian berikutnya
                - Transfer bank untuk refund tunai

                Barang yang Tidak Bisa Dikembalikan:
                - Barang personal (pakaian dalam, kosmetik)
                - Barang digital (e-book, software)
                - Barang custom/pesan khusus
                - Barang promo/diskon
                """
            }
        ]
        
        total_uploaded = 0
        
        for doc in sample_documents:
            print(f"📄 Processing {doc['filename']}...")
            
            # Process document
            chunks = ds.chunk_text(doc['content'], {'filename': doc['filename']})
            print(f"   ✅ Created {len(chunks)} chunks")
            
            # Upload ke vector store
            ids = vs.add_documents(chunks, collection_name=settings.DB_SCHEMA)
            print(f"   ✅ Uploaded {len(ids)} documents to collection '{settings.DB_SCHEMA}'")
            
            total_uploaded += len(ids)
        
        print(f"\n🎉 Setup completed! Total documents uploaded: {total_uploaded}")
        
        # Test retrieval
        print("\n🧪 Testing retrieval...")
        from app.services.rag.retriever import retrieve_knowledge
        
        test_queries = [
            "loyalty program",
            "payment methods", 
            "shipping information",
            "return policy"
        ]
        
        for query in test_queries:
            result = retrieve_knowledge(query)
            print(f"   Query: '{query}' -> Found {len(result)} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_status():
    """Check status database"""
    print("\n🔍 Checking database status...")
    
    try:
        from app.services.vectorstore_service import VectorStoreService
        from app.config import get_settings
        
        settings = get_settings()
        vs = VectorStoreService()
        
        # Check collection stats
        stats = vs.get_collection_stats(collection_name=settings.DB_SCHEMA)
        print(f"   Collection '{stats['collection']}': {stats['total_vectors']} documents")
        
        return stats['total_vectors'] > 0
        
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 RAG Database Setup Script")
    print("=" * 50)
    
    # Check if database already has data
    if check_database_status():
        print("✅ Database already has data!")
        return
    
    # Setup sample data
    if setup_sample_data():
        print("\n✅ Setup completed successfully!")
        print("🎯 RAG system is ready to use!")
    else:
        print("\n❌ Setup failed!")
        print("🔧 Please check your database connection and try again.")

if __name__ == "__main__":
    main()