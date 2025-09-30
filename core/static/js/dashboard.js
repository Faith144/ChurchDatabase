// Global action handlers for all pages
$(document).ready(function() {
    initializeAllActions();
    initializeFormHandlers();
});

function initializeAllActions() {
    // View Member Details
    $(document).on('click', '.view-member', function(e) {
        e.preventDefault();
        const memberId = $(this).data('member-id');
        showMemberDetails(memberId);
    });

    // Edit Member
    $(document).on('click', '.edit-member', function(e) {
        e.preventDefault();
        const memberId = $(this).data('member-id');
        loadMemberForm(memberId);
    });

    // Delete Member
    $(document).on('click', '.delete-member', function(e) {
        e.preventDefault();
        const memberId = $(this).data('member-id');
        const memberName = $(this).data('member-name');
        showDeleteConfirmation(memberId, memberName, 'member');
    });

    // View Family Details
    $(document).on('click', '.view-family', function(e) {
        e.preventDefault();
        const familyId = $(this).data('family-id');
        showFamilyDetails(familyId);
    });

    // Edit Family
    $(document).on('click', '.edit-family', function(e) {
        e.preventDefault();
        const familyId = $(this).data('family-id');
        loadFamilyForm(familyId);
    });

    // Delete Family
    $(document).on('click', '.delete-family', function(e) {
        e.preventDefault();
        const familyId = $(this).data('family-id');
        const familyName = $(this).data('family-name');
        showDeleteConfirmation(familyId, familyName, 'family');
    });

    // View Unit Details
    $(document).on('click', '.view-unit', function(e) {
        e.preventDefault();
        const unitId = $(this).data('unit-id');
        showUnitDetails(unitId);
    });

    // Edit Unit
    $(document).on('click', '.edit-unit', function(e) {
        e.preventDefault();
        const unitId = $(this).data('unit-id');
        loadUnitForm(unitId);
    });

    // Delete Unit
    $(document).on('click', '.delete-unit', function(e) {
        e.preventDefault();
        const unitId = $(this).data('unit-id');
        const unitName = $(this).data('unit-name');
        showDeleteConfirmation(unitId, unitName, 'unit');
    });

    // View Cell Details
    $(document).on('click', '.view-cell', function(e) {
        e.preventDefault();
        const cellId = $(this).data('cell-id');
        showCellDetails(cellId);
    });

    // Edit Cell
    $(document).on('click', '.edit-cell', function(e) {
        e.preventDefault();
        const cellId = $(this).data('cell-id');
        loadCellForm(cellId);
    });

    // Delete Cell
    $(document).on('click', '.delete-cell', function(e) {
        e.preventDefault();
        const cellId = $(this).data('cell-id');
        const cellName = $(this).data('cell-name');
        showDeleteConfirmation(cellId, cellName, 'cell');
    });

    // View Assembly Details
    $(document).on('click', '.view-assembly', function(e) {
        e.preventDefault();
        const assemblyId = $(this).data('assembly-id');
        showAssemblyDetails(assemblyId);
    });

    // Edit Assembly
    $(document).on('click', '.edit-assembly', function(e) {
        e.preventDefault();
        const assemblyId = $(this).data('assembly-id');
        loadAssemblyForm(assemblyId);
    });

    // Delete Assembly
    $(document).on('click', '.delete-assembly', function(e) {
        e.preventDefault();
        const assemblyId = $(this).data('assembly-id');
        const assemblyName = $(this).data('assembly-name');
        showDeleteConfirmation(assemblyId, assemblyName, 'assembly');
    });

    // Quick Action Buttons
    $('#addMemberBtn, #addMemberBtnEmpty').click(function(e) {
        e.preventDefault();
        loadMemberForm();
    });

    $('#addFamilyBtn, #addFamilyBtnEmpty').click(function(e) {
        e.preventDefault();
        loadFamilyForm();
    });

    $('#addUnitBtn, #addUnitBtnEmpty').click(function(e) {
        e.preventDefault();
        loadUnitForm();
    });

    $('#addCellBtn, #addCellBtnEmpty').click(function(e) {
        e.preventDefault();
        loadCellForm();
    });

    $('#addAssemblyBtn, #addAssemblyBtnEmpty').click(function(e) {
        e.preventDefault();
        loadAssemblyForm();
    });

    // Bulk Actions
    $('#bulkDelete').click(function(e) {
        e.preventDefault();
        const selectedMembers = $('.member-checkbox:checked').map(function() {
            return $(this).val();
        }).get();
        
        if (selectedMembers.length > 0) {
            showBulkDeleteConfirmation(selectedMembers, 'member');
        }
    });
}

// Member Functions
function showMemberDetails(memberId) {
    $.get(`/ajax/members/${memberId}/`, function(data) {
        $('#modalContainer').html(data.html);
        $('#memberDetailModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load member details:', xhr.responseText);
        showToast('error', 'Failed to load member details.');
    });
}

function loadMemberForm(memberId = null) {
    const url = memberId ? `/ajax/members/form/${memberId}/` : '/ajax/members/form/';
    
    $.get(url, function(data) {
        $('#modalContainer').html(data.html);
        $('#memberFormModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load member form:', xhr.responseText);
        showToast('error', 'Failed to load member form. Please try again.');
    });
}

// Family Functions
function showFamilyDetails(familyId) {
    $.get(`/ajax/families/${familyId}/`, function(data) {
        $('#modalContainer').html(data.html);
        $('#familyDetailModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load family details:', xhr.responseText);
        showToast('error', 'Failed to load family details.');
    });
}

function loadFamilyForm(familyId = null) {
    const url = familyId ? `/ajax/families/form/${familyId}/` : '/ajax/families/form/';
    
    $.get(url, function(data) {
        $('#modalContainer').html(data.html);
        $('#familyFormModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load family form:', xhr.responseText);
        showToast('error', 'Failed to load family form. Please try again.');
    });
}

// Cell Functions
function showCellDetails(cellId) {
    // Load cell details via AJAX
    $.get(`/ajax/cells/${cellId}/`, function(data) {
        $('#modalContainer').html(data.html);
        $('#cellDetailModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load cell details:', xhr.responseText);
        // Fallback to simple modal
        const modalHtml = `
            <div class="modal fade" id="cellDetailModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Cell Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Loading cell details...</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#modalContainer').html(modalHtml);
        $('#cellDetailModal').modal('show');
    });
}

function loadCellForm(cellId = null) {
    const url = cellId ? `/ajax/cells/form/${cellId}/` : '/ajax/cells/form/';
    
    $.get(url, function(data) {
        $('#modalContainer').html(data.html);
        $('#cellFormModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load cell form:', xhr.responseText);
        showToast('error', 'Failed to load cell form. Please try again.');
    });
}

// Assembly Functions
function showAssemblyDetails(assemblyId) {
    // Load assembly details via AJAX
    $.get(`/ajax/assemblies/${assemblyId}/`, function(data) {
        $('#modalContainer').html(data.html);
        $('#assemblyDetailModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load assembly details:', xhr.responseText);
        // Fallback to simple modal
        const modalHtml = `
            <div class="modal fade" id="assemblyDetailModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Assembly Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Loading assembly details...</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#modalContainer').html(modalHtml);
        $('#assemblyDetailModal').modal('show');
    });
}

function loadAssemblyForm(assemblyId = null) {
    const url = assemblyId ? `/ajax/assemblies/form/${assemblyId}/` : '/ajax/assemblies/form/';
    
    $.get(url, function(data) {
        $('#modalContainer').html(data.html);
        $('#assemblyFormModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load assembly form:', xhr.responseText);
        showToast('error', 'Failed to load assembly form. Please try again.');
    });
}

// Unit Functions
function showUnitDetails(unitId) {
    // Load unit details via AJAX
    $.get(`/ajax/units/${unitId}/`, function(data) {
        $('#modalContainer').html(data.html);
        $('#unitDetailModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load unit details:', xhr.responseText);
        // Fallback to simple modal
        const modalHtml = `
            <div class="modal fade" id="unitDetailModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Unit Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>Loading unit details...</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        $('#modalContainer').html(modalHtml);
        $('#unitDetailModal').modal('show');
    });
}

function loadUnitForm(unitId = null) {
    const url = unitId ? `/ajax/units/form/${unitId}/` : '/ajax/units/form/';
    
    $.get(url, function(data) {
        $('#modalContainer').html(data.html);
        $('#unitFormModal').modal('show');
    }).fail(function(xhr) {
        console.error('Failed to load unit form:', xhr.responseText);
        showToast('error', 'Failed to load unit form. Please try again.');
    });
}

// Delete Confirmation
function showDeleteConfirmation(objectId, objectName, objectType) {
    const message = `Are you sure you want to delete ${objectName}?`;
    const modalHtml = `
        <div class="modal fade" id="deleteConfirmationModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title text-danger">Confirm Deletion</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${message}
                        </p>
                        <p class="text-muted">This action cannot be undone.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirmDeleteBtn" data-object-id="${objectId}" data-object-type="${objectType}">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('#modalContainer').html(modalHtml);
    $('#deleteConfirmationModal').modal('show');

    $('#confirmDeleteBtn').on('click', function() {
        const objectId = $(this).data('object-id');
        const objectType = $(this).data('object-type');
        deleteObject(objectId, objectType);
    });
}

// Delete Single Object
function deleteObject(objectId, objectType) {
    const url = `/ajax/${objectType}s/delete/${objectId}/`;
    
    $.ajax({
        url: url,
        type: 'POST',
        success: function(response) {
            if (response.success) {
                $('#deleteConfirmationModal').modal('hide');
                showToast('success', response.message);
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
        },
        error: function(xhr) {
            console.error('Delete failed:', xhr.responseText);
            showToast('error', 'Failed to delete. Please try again.');
            $('#deleteConfirmationModal').modal('hide');
        }
    });
}

// Toast Notification Function
function showToast(type, message) {
    // Remove any existing toasts first
    $('.toast').remove();
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-triangle' : 
                 type === 'warning' ? 'exclamation-triangle' : 'info-circle';
    
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'info'} border-0 position-fixed top-0 end-0 m-3" role="alert" style="z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function initializeFormHandlers() {
    // Form handlers are initialized in their respective modal templates
}