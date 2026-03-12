window.LS = {
  badgeClass(status) {
    return {
      new: 'bg-danger',
      under_verification: 'bg-warning text-dark',
      confirmed: 'bg-success',
      false_positive: 'bg-secondary',
      closed: 'bg-dark'
    }[status] || 'bg-primary';
  }
};
