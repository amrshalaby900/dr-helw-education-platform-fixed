document.addEventListener("DOMContentLoaded", function() {
    // بيانات تجريبية للتقارير
    const sampleReports = [
        { id: 1, title: "تقرير أداء الطلاب - الفصل الأول", type: "students", date: "2025-05-01", status: "completed" },
        { id: 2, title: "تقرير حضور المحاضرات", type: "students", date: "2025-05-05", status: "active" },
        { id: 3, title: "تقرير نتائج الاختبارات النصفية", type: "quizzes", date: "2025-04-20", status: "completed" },
        { id: 4, title: "تقرير تقدم المقررات", type: "courses", date: "2025-05-10", status: "active" },
        { id: 5, title: "تقرير المستخدمين الجدد", type: "students", date: "2025-05-12", status: "pending" },
        { id: 6, title: "تقرير تفاعل الطلاب", type: "students", date: "2025-04-25", status: "completed" },
        { id: 7, title: "تقرير الاختبارات القادمة", type: "quizzes", date: "2025-05-15", status: "pending" },
        { id: 8, title: "تقرير تحليل أداء المقررات", type: "courses", date: "2025-04-30", status: "completed" }
    ];

    let currentReports = [...sampleReports];
    const reportsPerPage = 5;
    let currentPage = 1;

    // تحميل التقارير عند تحميل الصفحة
    loadReports();

    // تطبيق الفلاتر عند النقر على زر التطبيق
    document.getElementById("apply-filters-btn").addEventListener("click", function() {
        applyFilters();
    });

    // البحث في التقارير
    document.getElementById("search-btn").addEventListener("click", function() {
        applyFilters();
    });

    // البحث عند الضغط على Enter
    document.getElementById("search-input").addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            applyFilters();
        }
    });

    // تصدير التقارير كـ PDF
    document.getElementById("export-pdf-btn").addEventListener("click", function() {
        exportToPDF();
    });

    // تطبيق الفلاتر والبحث
    function applyFilters() {
        const typeFilter = document.getElementById("filter-type").value;
        const dateFilter = document.getElementById("filter-date").value;
        const statusFilter = document.getElementById("filter-status").value;
        const searchQuery = document.getElementById("search-input").value.toLowerCase();

        currentReports = sampleReports.filter(report => {
            // تطبيق فلتر النوع
            if (typeFilter !== "all" && report.type !== typeFilter) {
                return false;
            }

            // تطبيق فلتر التاريخ
            if (dateFilter && report.date !== dateFilter) {
                return false;
            }

            // تطبيق فلتر الحالة
            if (statusFilter !== "all" && report.status !== statusFilter) {
                return false;
            }

            // تطبيق البحث
            if (searchQuery && !report.title.toLowerCase().includes(searchQuery)) {
                return false;
            }

            return true;
        });

        currentPage = 1;
        loadReports();
    }

    // تحميل التقارير في الجدول
    function loadReports() {
        const tableBody = document.getElementById("reports-table-body");
        tableBody.innerHTML = "";

        // حساب التقارير للصفحة الحالية
        const startIndex = (currentPage - 1) * reportsPerPage;
        const endIndex = Math.min(startIndex + reportsPerPage, currentReports.length);
        const paginatedReports = currentReports.slice(startIndex, endIndex);

        if (paginatedReports.length === 0) {
            const emptyRow = document.createElement("tr");
            emptyRow.innerHTML = `<td colspan="6" style="text-align: center;">لا توجد تقارير متطابقة مع معايير البحث</td>`;
            tableBody.appendChild(emptyRow);
        } else {
            paginatedReports.forEach(report => {
                const row = document.createElement("tr");
                
                // تحديد لون الحالة
                let statusClass = "";
                let statusText = "";
                switch(report.status) {
                    case "active":
                        statusClass = "status-active";
                        statusText = "نشط";
                        break;
                    case "completed":
                        statusClass = "status-completed";
                        statusText = "مكتمل";
                        break;
                    case "pending":
                        statusClass = "status-pending";
                        statusText = "قيد الانتظار";
                        break;
                }
                
                row.innerHTML = `
                    <td>${report.id}</td>
                    <td>${report.title}</td>
                    <td>${getReportTypeName(report.type)}</td>
                    <td>${formatDate(report.date)}</td>
                    <td><span class="${statusClass}">${statusText}</span></td>
                    <td>
                        <button class="view-btn" data-id="${report.id}"><i class="fas fa-eye"></i></button>
                        <button class="export-single-btn" data-id="${report.id}"><i class="fas fa-file-pdf"></i></button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // إضافة مستمعي الأحداث لأزرار العرض والتصدير
            document.querySelectorAll(".view-btn").forEach(btn => {
                btn.addEventListener("click", function() {
                    const reportId = this.getAttribute("data-id");
                    viewReport(reportId);
                });
            });

            document.querySelectorAll(".export-single-btn").forEach(btn => {
                btn.addEventListener("click", function() {
                    const reportId = this.getAttribute("data-id");
                    exportSingleReport(reportId);
                });
            });
        }

        // تحديث الترقيم الصفحي
        updatePagination();
    }

    // تحديث الترقيم الصفحي
    function updatePagination() {
        const paginationContainer = document.getElementById("pagination-container");
        paginationContainer.innerHTML = "";

        const totalPages = Math.ceil(currentReports.length / reportsPerPage);
        
        if (totalPages <= 1) {
            return;
        }

        // زر الصفحة السابقة
        const prevButton = document.createElement("button");
        prevButton.innerHTML = "&laquo;";
        prevButton.disabled = currentPage === 1;
        prevButton.addEventListener("click", function() {
            if (currentPage > 1) {
                currentPage--;
                loadReports();
            }
        });
        paginationContainer.appendChild(prevButton);

        // أزرار الصفحات
        for (let i = 1; i <= totalPages; i++) {
            const pageButton = document.createElement("button");
            pageButton.textContent = i;
            if (i === currentPage) {
                pageButton.classList.add("active");
            }
            pageButton.addEventListener("click", function() {
                currentPage = i;
                loadReports();
            });
            paginationContainer.appendChild(pageButton);
        }

        // زر الصفحة التالية
        const nextButton = document.createElement("button");
        nextButton.innerHTML = "&raquo;";
        nextButton.disabled = currentPage === totalPages;
        nextButton.addEventListener("click", function() {
            if (currentPage < totalPages) {
                currentPage++;
                loadReports();
            }
        });
        paginationContainer.appendChild(nextButton);
    }

    // عرض تقرير محدد
    function viewReport(reportId) {
        const report = sampleReports.find(r => r.id == reportId);
        if (report) {
            alert(`عرض التقرير: ${report.title}`);
            // هنا يمكن إضافة كود لعرض التقرير بشكل تفصيلي
        }
    }

    // تصدير تقرير واحد
    function exportSingleReport(reportId) {
        const report = sampleReports.find(r => r.id == reportId);
        if (report) {
            alert(`جاري تصدير التقرير: ${report.title}`);
            // هنا سيتم استدعاء API لتصدير التقرير كـ PDF
            simulateExportToPDF([report]);
        }
    }

    // تصدير جميع التقارير المعروضة حالياً
    function exportToPDF() {
        if (currentReports.length === 0) {
            alert("لا توجد تقارير لتصديرها");
            return;
        }
        
        alert(`جاري تصدير ${currentReports.length} تقارير كملف PDF`);
        // هنا سيتم استدعاء API لتصدير التقارير كـ PDF
        simulateExportToPDF(currentReports);
    }

    // محاكاة تصدير PDF (سيتم استبدالها بالتنفيذ الفعلي)
    function simulateExportToPDF(reports) {
        // في التنفيذ الفعلي، سيتم إرسال طلب للخادم لإنشاء ملف PDF
        console.log("تصدير التقارير التالية كـ PDF:", reports);
        
        // محاكاة تأخير التحميل
        setTimeout(() => {
            alert("تم تصدير التقارير بنجاح!");
        }, 1500);
    }

    // تنسيق التاريخ
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-EG');
    }

    // الحصول على اسم نوع التقرير
    function getReportTypeName(type) {
        switch(type) {
            case "students": return "تقرير الطلاب";
            case "courses": return "تقرير المقررات";
            case "quizzes": return "تقرير الاختبارات";
            default: return type;
        }
    }
});

// إضافة أنماط CSS للحالات
document.addEventListener("DOMContentLoaded", function() {
    const style = document.createElement('style');
    style.textContent = `
        .status-active {
            background-color: #4CAF50;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
        }
        .status-completed {
            background-color: #2196F3;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
        }
        .status-pending {
            background-color: #FF9800;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
        }
        .view-btn, .export-single-btn {
            background: none;
            border: none;
            cursor: pointer;
            margin: 0 3px;
            font-size: 16px;
        }
        .view-btn {
            color: #2196F3;
        }
        .export-single-btn {
            color: #4CAF50;
        }
    `;
    document.head.appendChild(style);
});
