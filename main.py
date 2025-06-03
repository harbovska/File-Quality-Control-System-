import streamlit as st
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
from datetime import datetime
import os

# Налаштування сторінки
st.set_page_config(
    page_title="Система Контролю Якості Файлів",
    page_icon="🖨️",
    layout="wide"
)

# CSS стилі
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Заголовок
    st.markdown("""
    <div class="main-header">
        <h1>🖨️ Система Контролю Якості Файлів</h1>
        <h3>Професійна перевірка файлів для друкарської індустрії</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Інформація про фотодрук
    st.markdown("""
    <div class="feature-box">
        <h2>📸 Про Фотодрук та Якість Файлів</h2>
        <p><strong>Фотодрук</strong> - це процес створення фізичних зображень з цифрових файлів. Для отримання високоякісних результатів критично важливо дотримуватися технічних вимог:</p>
        
        <h4>🎯 Основні вимоги до файлів:</h4>
        <ul>
            <li><strong>Формат файлу:</strong> JPEG - найпоширеніший формат для фотодруку</li>
            <li><strong>Роздільна здатність:</strong> Мінімум 300 DPI для якісного друку</li>
            <li><strong>Колірна модель:</strong> RGB - стандарт для цифрових зображень</li>
        </ul>
        
        <h4>⚡ Переваги нашої системи:</h4>
        <ul>
            <li>Автоматична перевірка технічних параметрів</li>
            <li>ШІ-покращення файлів при виявленні недоліків</li>
            <li>Детальні звіти про якість</li>
            <li>Можливість завантаження покращених файлів</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Завантаження файлів
    st.markdown("## 📁 Завантаження Файлів")
    uploaded_files = st.file_uploader(
        "Оберіть файли для перевірки",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        accept_multiple_files=True,
        help="Підтримувані формати: JPG, JPEG, PNG, BMP, TIFF"
    )
    
    if uploaded_files:
        st.success(f"✅ Завантажено {len(uploaded_files)} файл(ів)")
        
        # Кнопка перевірки
        if st.button("🔍 ПЕРЕВІРИТИ ФАЙЛИ", type="primary", use_container_width=True):
            results = []
            
            # Прогрес бар
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Перевірка файлу: {uploaded_file.name}")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Аналіз файлу
                result = analyze_file(uploaded_file)
                results.append(result)
            
            status_text.text("Перевірка завершена!")
            
            # Відображення результатів
            display_results(results, uploaded_files)
            
            # Генерація звіту
            generate_report(results)

def analyze_file(uploaded_file):
    """Аналіз файлу на відповідність вимогам"""
    try:
        # Відкриття зображення
        image = Image.open(uploaded_file)
        
        # Перевірка формату
        format_check = uploaded_file.type == "image/jpeg"
        
        # Перевірка DPI
        dpi = image.info.get('dpi', (72, 72))
        if isinstance(dpi, tuple):
            dpi_value = min(dpi)
        else:
            dpi_value = dpi
        dpi_check = dpi_value >= 300
        
        # Перевірка колірної моделі
        color_mode = image.mode
        rgb_check = color_mode in ['RGB', 'RGBA']
        
        # Розмір файлу
        file_size = len(uploaded_file.getvalue())
        
        # Розміри зображення
        width, height = image.size
        
        # Загальна оцінка
        issues = []
        if not format_check:
            issues.append("Неправильний формат файлу")
        if not dpi_check:
            issues.append(f"Низька роздільна здатність ({dpi_value} DPI)")
        if not rgb_check:
            issues.append(f"Неправильна колірна модель ({color_mode})")
        
        overall_quality = "Відмінно" if not issues else "Потребує покращення"
        
        return {
            'filename': uploaded_file.name,
            'format_check': format_check,
            'dpi_check': dpi_check,
            'dpi_value': dpi_value,
            'rgb_check': rgb_check,
            'color_mode': color_mode,
            'file_size': file_size,
            'width': width,
            'height': height,
            'issues': issues,
            'overall_quality': overall_quality,
            'image': image
        }
    except Exception as e:
        return {
            'filename': uploaded_file.name,
            'error': str(e),
            'overall_quality': 'Помилка'
        }

def display_results(results, uploaded_files):
    """Відображення результатів перевірки"""
    st.markdown("## 📊 Результати Перевірки")
    
    for i, result in enumerate(results):
        with st.expander(f"📄 {result['filename']}", expanded=True):
            if 'error' in result:
                st.markdown(f"""
                <div class="error-box">
                    <strong>❌ Помилка:</strong> {result['error']}
                </div>
                """, unsafe_allow_html=True)
                continue
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Результати перевірки
                st.markdown("### 🔍 Результати Аналізу")
                
                # Формат файлу
                format_status = "✅ Пройдено" if result['format_check'] else "❌ Не пройдено"
                st.markdown(f"**Формат файлу (JPEG):** {format_status}")
                
                # DPI
                dpi_status = "✅ Пройдено" if result['dpi_check'] else "❌ Не пройдено"
                st.markdown(f"**Роздільна здатність (≥300 DPI):** {dpi_status} ({result['dpi_value']} DPI)")
                
                # RGB
                rgb_status = "✅ Пройдено" if result['rgb_check'] else "❌ Не пройдено"
                st.markdown(f"**Колірна модель (RGB):** {rgb_status} ({result['color_mode']})")
                
                # Загальна інформація
                st.markdown("### 📏 Технічні Характеристики")
                st.markdown(f"**Розміри:** {result['width']} x {result['height']} пікселів")
                st.markdown(f"**Розмір файлу:** {result['file_size'] / 1024:.1f} KB")
                
                # Загальна оцінка
                if result['overall_quality'] == "Відмінно":
                    st.markdown("""
                    <div class="success-box">
                        <strong>✅ Загальна оцінка: Відмінно</strong><br>
                        Файл відповідає всім вимогам для якісного друку.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    issues_text = "<br>• ".join(result['issues'])
                    st.markdown(f"""
                    <div class="warning-box">
                        <strong>⚠️ Загальна оцінка: Потребує покращення</strong><br>
                        Виявлені проблеми:<br>• {issues_text}
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Превью зображення
                st.markdown("### 🖼️ Превью")
                st.image(result['image'], use_container_width=True)
                
                # ШІ покращення
                if result['issues']:
                    st.markdown("### 🤖 ШІ Покращення")
                    if st.button(f"Покращити файл", key=f"improve_{i}"):
                        improved_image = improve_image_ai(result['image'], result['issues'])
                        st.success("✅ Файл покращено!")
                        
                        # Показати покращене зображення
                        st.markdown("**Покращений файл:**")
                        st.image(improved_image, use_container_width=True)
                        
                        # Кнопка завантаження
                        img_buffer = io.BytesIO()
                        improved_image.save(img_buffer, format='JPEG', quality=95, dpi=(300, 300))
                        img_buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Завантажити покращений файл",
                            data=img_buffer.getvalue(),
                            file_name=f"improved_{result['filename']}",
                            mime="image/jpeg"
                        )

def improve_image_ai(image, issues):
    """Симуляція ШІ покращення зображення"""
    improved = image.copy()
    
    # Конвертація в RGB якщо потрібно
    if improved.mode != 'RGB':
        improved = improved.convert('RGB')
    
    # Покращення якості
    if any("роздільна здатність" in issue.lower() for issue in issues):
        # Збільшення роздільної здатності
        width, height = improved.size
        new_width = int(width * 1.5)
        new_height = int(height * 1.5)
        improved = improved.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Покращення кольорів та контрасту
    enhancer = ImageEnhance.Color(improved)
    improved = enhancer.enhance(1.1)
    
    enhancer = ImageEnhance.Contrast(improved)
    improved = enhancer.enhance(1.05)
    
    enhancer = ImageEnhance.Sharpness(improved)
    improved = enhancer.enhance(1.1)
    
    return improved

def generate_report(results):
    """Генерація звіту в Excel"""
    st.markdown("## 📋 Звіт про Перевірку")
    
    # Підготовка даних для звіту
    report_data = []
    for result in results:
        if 'error' not in result:
            report_data.append({
                'Назва файлу': result['filename'],
                'Формат JPEG': 'Так' if result['format_check'] else 'Ні',
                'DPI': result['dpi_value'],
                'DPI ≥300': 'Так' if result['dpi_check'] else 'Ні',
                'Колірна модель': result['color_mode'],
                'RGB': 'Так' if result['rgb_check'] else 'Ні',
                'Ширина (px)': result['width'],
                'Висота (px)': result['height'],
                'Розмір файлу (KB)': round(result['file_size'] / 1024, 1),
                'Загальна оцінка': result['overall_quality'],
                'Проблеми': '; '.join(result['issues']) if result['issues'] else 'Немає'
            })
    
    if report_data:
        df = pd.DataFrame(report_data)
        
        # Відображення таблиці
        st.dataframe(df, use_container_width=True)
        
        # Статистика
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_files = len(report_data)
            st.metric("📁 Всього файлів", total_files)
        
        with col2:
            passed_files = len([r for r in results if r.get('overall_quality') == 'Відмінно'])
            st.metric("✅ Пройшли перевірку", passed_files)
        
        with col3:
            failed_files = total_files - passed_files
            st.metric("⚠️ Потребують покращення", failed_files)
        
        with col4:
            success_rate = (passed_files / total_files * 100) if total_files > 0 else 0
            st.metric("📊 Відсоток успіху", f"{success_rate:.1f}%")
        
        # Кнопка завантаження Excel звіту
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Звіт про якість файлів', index=False)
            
            # Додаткова статистика
            stats_df = pd.DataFrame({
                'Показник': ['Всього файлів', 'Пройшли перевірку', 'Потребують покращення', 'Відсоток успіху'],
                'Значення': [total_files, passed_files, failed_files, f"{success_rate:.1f}%"]
            })
            stats_df.to_excel(writer, sheet_name='Статистика', index=False)
        
        excel_buffer.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📥 Завантажити звіт Excel",
            data=excel_buffer.getvalue(),
            file_name=f"звіт_якості_файлів_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
