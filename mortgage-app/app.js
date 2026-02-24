// ─── Approval Thresholds ─────────────────────────────────────────────────────
const GDS_LIMIT    = 39;   // %
const TDS_LIMIT    = 44;   // %
const DOWN_MIN_PCT =  5;   // %
const DOWN_MAX_PCT = 20;   // %
const MIN_CREDIT   = 650;

// ─── Helpers ─────────────────────────────────────────────────────────────────
function fmt(n) {
  return '$' + Math.round(n).toLocaleString('en-CA');
}

function pct(n) {
  return n.toFixed(1) + '%';
}

function getVal(id) {
  return parseFloat(document.getElementById(id).value) || 0;
}

/**
 * Monthly mortgage payment using standard amortization formula.
 * M = P * [r(1+r)^n] / [(1+r)^n - 1]
 */
function monthlyPayment(principal, annualRate, years) {
  if (annualRate === 0) return principal / (years * 12);
  const r = annualRate / 100 / 12;
  const n = years * 12;
  return principal * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
}

// ─── Main Logic ───────────────────────────────────────────────────────────────
function checkApproval() {
  // Gather inputs
  const annualIncome   = getVal('income');
  const creditScore    = getVal('credit-score');
  const purchasePrice  = getVal('purchase-price');
  const downPayment    = getVal('down-payment');
  const interestRate   = getVal('interest-rate');
  const amortization   = parseInt(document.getElementById('amortization').value);
  const propTaxes      = getVal('prop-taxes');
  const heating        = getVal('heating');
  const condoFees      = getVal('condo-fees');
  const otherDebts     = getVal('other-debts');

  // Basic validation
  if (!annualIncome || !creditScore || !purchasePrice || !downPayment) {
    alert('Please fill in all required fields.');
    return;
  }

  // Derived values
  const monthlyIncome   = annualIncome / 12;
  const mortgageAmount  = purchasePrice - downPayment;
  const monthlyMortgage = monthlyPayment(mortgageAmount, interestRate, amortization);
  const condoHalf       = condoFees * 0.5;
  const downPct         = (downPayment / purchasePrice) * 100;

  // Housing costs (used in GDS)
  const monthlyHousing = monthlyMortgage + propTaxes + heating + condoHalf;

  // GDS = Housing costs / Gross monthly income
  const gds = (monthlyHousing / monthlyIncome) * 100;

  // TDS = (Housing costs + other debts) / Gross monthly income
  const totalObligations = monthlyHousing + otherDebts;
  const tds = (totalObligations / monthlyIncome) * 100;

  // ─── Evaluate each criterion ─────────────────────────────────────────────
  const passGDS    = gds <= GDS_LIMIT;
  const passTDS    = tds <= TDS_LIMIT;
  const passDown   = downPct >= DOWN_MIN_PCT && downPct <= DOWN_MAX_PCT;
  const passCredit = creditScore >= MIN_CREDIT;
  const approved   = passGDS && passTDS && passDown && passCredit;

  // ─── Render Results ───────────────────────────────────────────────────────
  const resultSection = document.getElementById('result-section');
  resultSection.style.display = 'block';
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Banner
  const banner = document.getElementById('result-banner');
  banner.className = 'result-banner ' + (approved ? 'approved' : 'declined');
  document.getElementById('result-icon').textContent  = approved ? '✓' : '✗';
  document.getElementById('result-title').textContent =
    approved ? 'Pre-Approved!' : 'Not Pre-Approved';
  document.getElementById('result-subtitle').textContent = approved
    ? 'Congratulations! You meet all the requirements for mortgage pre-approval.'
    : 'Unfortunately, you do not meet one or more of the approval requirements.';

  // GDS Card
  setMetric('gds', pct(gds), Math.min((gds / GDS_LIMIT) * 100, 100), passGDS,
    passGDS ? `Pass — ${pct(gds)} is within the 39% limit` : `Fail — ${pct(gds)} exceeds the 39% limit`);

  // TDS Card
  setMetric('tds', pct(tds), Math.min((tds / TDS_LIMIT) * 100, 100), passTDS,
    passTDS ? `Pass — ${pct(tds)} is within the 44% limit` : `Fail — ${pct(tds)} exceeds the 44% limit`);

  // Down Payment Card
  setMetric('down', pct(downPct), Math.min((downPct / 20) * 100, 100), passDown,
    passDown
      ? `Pass — ${pct(downPct)} is within the 5%–20% range`
      : downPct < DOWN_MIN_PCT
        ? `Fail — ${pct(downPct)} is below the 5% minimum`
        : `Fail — ${pct(downPct)} exceeds the 20% maximum (consider a conventional mortgage)`);

  // Credit Card
  const creditBarPct = Math.min(((creditScore - 300) / (900 - 300)) * 100, 100);
  setMetric('credit', creditScore, creditBarPct, passCredit,
    passCredit ? `Pass — Score of ${creditScore} meets the 650 minimum` : `Fail — Score of ${creditScore} is below the 650 minimum`);

  // Summary
  document.getElementById('s-mortgage').textContent    = fmt(mortgageAmount);
  document.getElementById('s-monthly').textContent     = fmt(monthlyMortgage) + '/mo';
  document.getElementById('s-income').textContent      = fmt(monthlyIncome) + '/mo';
  document.getElementById('s-housing').textContent     = fmt(monthlyHousing) + '/mo';
  document.getElementById('s-obligations').textContent = fmt(totalObligations) + '/mo';
  document.getElementById('s-rate').textContent        = pct(interestRate);

  // Issues list
  const issues = [];
  if (!passGDS)    issues.push(`GDS ratio of ${pct(gds)} exceeds the maximum allowed 39%.`);
  if (!passTDS)    issues.push(`TDS ratio of ${pct(tds)} exceeds the maximum allowed 44%.`);
  if (!passDown)   issues.push(
    downPct < DOWN_MIN_PCT
      ? `Down payment of ${pct(downPct)} is below the minimum 5% requirement.`
      : `Down payment of ${pct(downPct)} is above 20% — consider a conventional mortgage lender.`
  );
  if (!passCredit) issues.push(`Credit score of ${creditScore} is below the minimum required score of 650.`);

  const issuesSection = document.getElementById('issues-section');
  const issuesList    = document.getElementById('issues-list');
  if (issues.length > 0) {
    issuesSection.style.display = 'block';
    issuesList.innerHTML = issues.map(i => `<li>${i}</li>`).join('');
  } else {
    issuesSection.style.display = 'none';
  }
}

function setMetric(id, value, barPct, pass, statusText) {
  const card   = document.getElementById('card-' + id);
  const valEl  = document.getElementById(id + '-value');
  const barEl  = document.getElementById(id + '-bar');
  const statEl = document.getElementById(id + '-status');

  card.className   = 'metric-card ' + (pass ? 'pass' : 'fail');
  valEl.textContent  = value;
  barEl.style.width  = barPct + '%';
  statEl.textContent = statusText;
}

function resetForm() {
  document.getElementById('result-section').style.display = 'none';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
