/* Employee Admin Tabbed Interface */
(function($) {
    'use strict';

    var TAB_DEFINITIONS = [
        { key: 'jobdata',  label: 'البيانات الوظيفية',      cls: 'tab-jobdata' },
        { key: 'status',   label: 'حالات الموظف',             cls: 'tab-status' },
        { key: 'bank',     label: 'الحسابات البنكية',        cls: 'tab-bank' },
        { key: 'leave',    label: 'الإجازات',                cls: 'tab-leave' },
        { key: 'penalty',  label: 'الجزاءات',                cls: 'tab-penalty' },
        { key: 'document', label: 'الأرشيف الرقمي',         cls: 'tab-document' },
        { key: 'salary',   label: 'تفاصيل المرتب',          cls: 'tab-salary' },
        { key: 'academic', label: 'المؤهلات الأكاديمية',    cls: 'tab-academic' },
    ];

    function initTabs() {
        // Find existing fieldsets (Basic Info) and Inlines
        var $inlineGroups = $('.inline-group');
        
        if (!$inlineGroups.length) return;

        // Build containers
        var $nav = $('<ul class="employee-tabs-nav"></ul>');
        var $container = $('<div id="employee-tabs-container"></div>');
        var tabsFound = [];

        // 2. Handle Inlines
        TAB_DEFINITIONS.forEach(function(tab) {
            if (tab.key === 'basic') return; 

            var $inlines = $('.inline-group.' + tab.cls + ', .inline-group [class*="' + tab.cls + '"]');


            // Fallback: check by header text (h2)
            if (!$inlines.length) {
                $inlines = $('.inline-group').filter(function() {
                    var h2Text = $(this).find('h2').text().trim();
                    return h2Text.indexOf(tab.label.split(' ')[0]) !== -1 || h2Text.indexOf(tab.label) !== -1;
                });
            }

            if ($inlines.length) {
                var $panel = $('<div class="employee-tab-panel" data-tab="' + tab.key + '"></div>');
                $inlines.each(function() {
                    $panel.append($(this).detach());
                });
                $container.append($panel);

                var $btn = $('<li><button type="button" class="tab-btn" data-tab="' + tab.key + '">' + tab.label + '</button></li>');
                $nav.append($btn);
                tabsFound.push(tab.key);
            }
        });

        if (!tabsFound.length) return;

        // Insert before the remaining form elements (submit row)
        $('.submit-row').first().before($nav).before($container);

        // Activate first tab
        activateTab(tabsFound[0]);

        // Click handler
        $nav.on('click', '.tab-btn', function() {
            activateTab($(this).data('tab'));
            // Reflow tables if using django-tables2 or similar
            $(window).trigger('resize');
        });
    }

    function activateTab(key) {
        $('.tab-btn').removeClass('active');
        $('.tab-btn[data-tab="' + key + '"]').addClass('active');
        $('.employee-tab-panel').removeClass('active');
        $('.employee-tab-panel[data-tab="' + key + '"]').addClass('active');
    }

    $(document).ready(function() {
        initTabs();
    });

})(django.jQuery);
