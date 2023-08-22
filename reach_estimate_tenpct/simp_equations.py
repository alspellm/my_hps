class SimpEquations:

    def __init__(self, year = 2016, alpha_dark = 0.01, mass_ratio_Ap_to_Vd = 1.66, mass_ratio_Ap_to_Pid = 3.0, 
        ratio_mPi_to_fPi = 12.566, lepton_mass = 0.511):
        self.year = year
        self.alpha_dark = alpha_dark
        self.mass_ratio_Ap_to_Vd = mass_ratio_Ap_to_V
        self.mass_ratio_Ap_to_Pid = mass_ratio_Ap_to_Pid
        self.ratio_mPi_to_fPi = ratio_mPi_to_fPi
        self.lepton_mass = lepton_mass

    @staticmethod
    def rate_2pi(m_Ap, m_pi, m_V, alpha_D):
        coeff = (2.0 * alpha_D / 3.0) * m_Ap
        pow1 = math.pow((1 - (4 * m_pi * m_pi / (m_Ap * m_Ap))), 3 / 2.0)
        pow2 = math.pow(((m_V * m_V) / ((m_Ap * m_Ap) - (m_V * m_V))), 2)
        return coeff * pow1 * pow2

    @staticmethod
    def rate_Vpi(m_Ap, m_pi, m_V, alpha_D, f_pi, rho, phi):
        x = m_pi / m_Ap
        y = m_V / m_Ap
        coeff = alpha_D * SimpEquations.Tv(rho, phi) / (192.0 * math.pow(math.pi, 4))
        return coeff * math.pow((m_Ap / m_pi), 2) * math.pow(m_V / m_pi, 2) * math.pow((m_pi / f_pi), 4) * m_Ap * math.pow(SimpEquations.Beta(x, y), 3 / 2.0)

    @staticmethod
    def br_Vpi(m_Ap, m_pi, m_V, alpha_D, f_pi, rho, phi):
        rate = SimpEquations.rate_Vpi(m_Ap, m_pi, m_V, alpha_D, f_pi, rho, phi) + SimpEquations.rate_2pi(m_Ap, m_pi, m_V, alpha_D)
        if 2 * m_V < m_Ap:
            rate += SimpEquations.rate_2V(m_Ap, m_V, alpha_D)
        return SimpEquations.rate_Vpi(m_Ap, m_pi, m_V, alpha_D, f_pi, rho, phi) / rate

    @staticmethod
    def br_2V(m_Ap, m_pi, m_V, alpha_D, f_pi, rho, phi):
        if 2 * m_V >= m_Ap:
            return 0.0
        rate = (
            SimpEquations.rate_Vpi(m_Ap, m_pi, m_V, alpha_D, f_pi, rho, phi)
            + SimpEquations.rate_2pi(m_Ap, m_pi, m_V, alpha_D)
            + SimpEquations.rate_2V(m_Ap, m_V, alpha_D)
        )
        return SimpEquations.rate_2V(m_Ap, m_V, alpha_D) / rate

    @staticmethod
    def Tv(rho, phi):
        if rho:
            return 3.0 / 4.0
        elif phi:
            return 3.0 / 2.0
        else:
            return 18.0

    @staticmethod
    def Beta(x, y):
        return (1 + math.pow(y, 2) - math.pow(x, 2) - 2 * y) * (1 + math.pow(y, 2) - math.pow(x, 2) + 2 * y)

    @staticmethod
    def rate_2V(m_Ap, m_V, alpha_D):
        r = m_V / m_Ap
        return alpha_D / 6.0 * m_Ap * SimpEquations.f(r)

    @staticmethod
    def f(r):
        # Define your function f(r) here
        # Example: return some_expression
        pass

    @staticmethod
    def rate_2l(m_Ap, m_pi, m_V, eps, alpha_D, f_pi, m_l, rho):
        alpha = 1.0 / 137.0
        coeff = (16 * math.pi * alpha_D * alpha * eps**2 * f_pi**2) / (3 * m_V**2)
        term1 = (m_V**2 / (m_Ap**2 - m_V**2))**2
        term2 = (1 - (4 * m_l**2 / m_V**2))**0.5
        term3 = 1 + (2 * m_l**2 / m_V**2)
        constant = 1 if not rho else 2
        return coeff * term1 * term2 * term3 * m_V * constant

    @staticmethod
    def getCtau(m_Ap, m_pi, m_V, eps, alpha_D, f_pi, m_l, rho):
        c = 3.00e10  # cm/s
        hbar = 6.58e-22  # MeV*sec
        rate = SimpEquations.rate_2l(m_Ap, m_pi, m_V, eps, alpha_D, f_pi, m_l, rho)  # MeV
        tau = hbar / rate
        ctau = c * tau
        return ctau

    @staticmethod
    def gamma(m_V, E_V):
        gamma = E_V / m_V
        return gamma

    def expectedSignalCalculation(self, m_V, eps, rho, phi, E_V, effCalc_h, target_pos, zcut):
        # Signal mass dependent SIMP parameters
        m_Ap = m_V * self.mass_ratio_Ap_to_Vd_
        m_pi = m_Ap / self.mass_ratio_Ap_to_Pid_
        f_pi = m_pi / self.ratio_mPi_to_fPi_

        # Mass in MeV
        ctau = self.getCtau(m_Ap, m_pi, m_V, eps, self.alpha_D_, f_pi, self.m_l_, rho)
        gcTau = ctau * self.gamma(m_V / 1000.0, E_V)  # E_V in GeV

        # Calculate the Efficiency Vertex (Displaced VD Acceptance)
        effVtx = 0.0
        for zbin in range(effCalc_h.GetTotalHistogram().GetNbinsX() + 1):
            zz = effCalc_h.GetTotalHistogram().GetBinLowEdge(zbin)
            if zz < zcut:
                continue
            effVtx += (math.exp((target_pos - zz) / gcTau) / gcTau) * \
                (effCalc_h.GetEfficiency(zbin) - effCalc_h.GetEfficiencyErrorLow(zbin)) * \
                effCalc_h.GetTotalHistogram().GetBinWidth(zbin)

        # Total A' Production Rate
        apProduction = (3. * 137 / 2.) * 3.14159 * (m_Ap * eps * eps * self.radiativeFraction(m_Ap) * self.controlRegionBackgroundRate(m_Ap)) \
            / self.radiativeAcceptance(m_Ap)

        # A' -> V+Pi Branching Ratio
        br_VPi = self.br_Vpi(m_Ap, m_pi, m_V, self.alpha_D_, f_pi, rho, phi)

        # Vector to e+e- BR = 1
        br_V_ee = 1.0

        # Expected Signal
        expSignal = apProduction * effVtx * br_VPi * br_V_ee

        return expSignal
