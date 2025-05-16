document.addEventListener("DOMContentLoaded", function() {
    // إنشاء زر واتساب العائم
    const whatsappButton = document.createElement('a');
    whatsappButton.href = 'https://wa.me/ais/9897460410335943?s=5';
    whatsappButton.className = 'whatsapp-float';
    whatsappButton.target = '_blank';
    whatsappButton.rel = 'noopener noreferrer';
    
    // إضافة أيقونة واتساب (باستخدام Font Awesome إذا كان متاحاً)
    const icon = document.createElement('i');
    icon.className = 'fa fa-whatsapp';
    
    // إضافة النص
    const text = document.createTextNode('دردش مع موسوعة الأحياء من د/محمد الحلو على واتساب');
    
    // تجميع العناصر
    whatsappButton.appendChild(icon);
    whatsappButton.appendChild(text);
    
    // إضافة الزر إلى الصفحة
    document.body.appendChild(whatsappButton);
});
