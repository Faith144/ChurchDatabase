    // <!-- Mobile Navigation JavaScript -->
    $(document).ready(function() {
        // Create mobile header and overlay if they don't exist
        if ($('.mobile-nav-header').length === 0) {
            $('body').prepend(`
                <div class="sidebar-overlay"></div>
                <div class="mobile-nav-header">
                    <button class="sidebar-toggle">
                        <i class="fas fa-bars"></i>
                    </button>
                    <div class="mobile-logo">
                        <img src="{% static 'images/logo.gif' %}" alt="SEPCAM Logo" style="height: 40px;">
                    </div>
                    <div style="width: 40px;"></div> <!-- Spacer for balance -->
                </div>
            `);
        }

        // Toggle sidebar
        $(document).on('click', '.sidebar-toggle', function() {
            $('.sidebar').addClass('show');
            $('.sidebar-overlay').addClass('show');
        });

        // Close sidebar when overlay is clicked
        $(document).on('click', '.sidebar-overlay', function() {
            $('.sidebar').removeClass('show');
            $('.sidebar-overlay').removeClass('show');
        });

        // Close sidebar when a nav link is clicked (on mobile)
        $('.sidebar .nav-link').on('click', function() {
            if ($(window).width() <= 768) {
                $('.sidebar').removeClass('show');
                $('.sidebar-overlay').removeClass('show');
            }
        });

        // Close sidebar on window resize if it becomes desktop view
        $(window).on('resize', function() {
            if ($(window).width() > 768) {
                $('.sidebar').removeClass('show');
                $('.sidebar-overlay').removeClass('show');
            }
        });
    });