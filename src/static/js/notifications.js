document.addEventListener("DOMContentLoaded", function() {
    // إنشاء حاوية الإشعارات
    const notificationContainer = document.createElement('div');
    notificationContainer.className = 'notification-container';
    document.body.appendChild(notificationContainer);

    // تعريف كائن عام للإشعارات
    window.NotificationSystem = {
        // أنواع الإشعارات
        types: {
            SUCCESS: 'success',
            ERROR: 'error',
            WARNING: 'warning',
            INFO: 'info'
        },
        
        // إظهار إشعار جديد
        show: function(title, message, type = 'info', duration = 5000) {
            // إنشاء عنصر الإشعار
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            
            // إضافة أيقونة حسب النوع
            let iconClass = '';
            switch(type) {
                case this.types.SUCCESS:
                    iconClass = 'fa-check-circle';
                    break;
                case this.types.ERROR:
                    iconClass = 'fa-exclamation-circle';
                    break;
                case this.types.WARNING:
                    iconClass = 'fa-exclamation-triangle';
                    break;
                case this.types.INFO:
                default:
                    iconClass = 'fa-info-circle';
                    break;
            }
            
            // بناء هيكل الإشعار
            notification.innerHTML = `
                <div class="notification-icon">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${title}</div>
                    <div class="notification-message">${message}</div>
                </div>
                <button class="notification-close">
                    <i class="fas fa-times"></i>
                </button>
                <div class="notification-progress"></div>
            `;
            
            // إضافة الإشعار إلى الحاوية
            notificationContainer.appendChild(notification);
            
            // إظهار الإشعار بعد إضافته (للتأثير الحركي)
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            // إضافة مستمع حدث لزر الإغلاق
            const closeButton = notification.querySelector('.notification-close');
            closeButton.addEventListener('click', () => {
                this.close(notification);
            });
            
            // تشغيل شريط التقدم
            const progressBar = notification.querySelector('.notification-progress');
            let width = 0;
            const interval = duration / 100;
            const progressInterval = setInterval(() => {
                width++;
                progressBar.style.width = width + '%';
                if (width >= 100) {
                    clearInterval(progressInterval);
                    this.close(notification);
                }
            }, interval);
            
            // إيقاف شريط التقدم عند تحويم الماوس
            notification.addEventListener('mouseenter', () => {
                clearInterval(progressInterval);
            });
            
            // استئناف شريط التقدم عند مغادرة الماوس
            notification.addEventListener('mouseleave', () => {
                let remainingWidth = 100 - parseInt(progressBar.style.width);
                let remainingTime = (remainingWidth / 100) * duration;
                
                const newInterval = remainingTime / remainingWidth;
                const newProgressInterval = setInterval(() => {
                    width++;
                    progressBar.style.width = width + '%';
                    if (width >= 100) {
                        clearInterval(newProgressInterval);
                        this.close(notification);
                    }
                }, newInterval);
                
                notification.addEventListener('mouseenter', () => {
                    clearInterval(newProgressInterval);
                });
            });
            
            return notification;
        },
        
        // إغلاق إشعار
        close: function(notification) {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        },
        
        // اختصارات لأنواع الإشعارات
        success: function(title, message, duration) {
            return this.show(title, message, this.types.SUCCESS, duration);
        },
        
        error: function(title, message, duration) {
            return this.show(title, message, this.types.ERROR, duration);
        },
        
        warning: function(title, message, duration) {
            return this.show(title, message, this.types.WARNING, duration);
        },
        
        info: function(title, message, duration) {
            return this.show(title, message, this.types.INFO, duration);
        }
    };
    
    // مثال على استخدام نظام الإشعارات (يمكن إزالته في الإنتاج)
    /*
    setTimeout(() => {
        window.NotificationSystem.success('نجاح', 'تم تسجيل الدخول بنجاح!');
    }, 1000);
    
    setTimeout(() => {
        window.NotificationSystem.error('خطأ', 'فشل الاتصال بالخادم، يرجى المحاولة مرة أخرى.');
    }, 3000);
    
    setTimeout(() => {
        window.NotificationSystem.warning('تنبيه', 'سيتم تسجيل خروجك تلقائياً بعد 5 دقائق من عدم النشاط.');
    }, 5000);
    
    setTimeout(() => {
        window.NotificationSystem.info('معلومة', 'تم إضافة محتوى جديد إلى المقرر.');
    }, 7000);
    */
});
