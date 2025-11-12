from dataclasses import dataclass
from typing import Dict, Any
import matplotlib.pyplot as plt  # For visualization in module 5
from beam_analysis import fixed_fixed_uniform_load, pinned_pinned_point_load, pinned_pinned_uniform_load, fixed_fixed_two_point_load, fixed_fixed_point_load

@dataclass
class DesignInputs:
    """Module 1: Design variables input as per PRD section 3.1"""
    # Design conditions
    x_span: float = 10.8  # column-to-column in x-dir. (m)
    y_span: float = 10.2  # column-to-column in y-dir. (m)
    slab_thickness: float = 0.2  # 슬래브 두께 (m)
    construction_live_load: float = 2.5  # 시공 LL (kN/m²)
    concrete_density: float = 24.0  # 콘크리트 비중 (kN/m³)
    
    # Geometry
    num_y_girders: int = 2  # y-dir beam count (affects tributary width)
    x_support_condition: str = 'fixed'  # 'pinned' or 'fixed' for x-dir
    y_support_condition: str = 'pinned'  # 'pinned' or 'fixed' for y-dir
    
    # Angle properties
    angle_fy: float  # 앵글 Fy (MPa)
    angle_es: float  # 앵글 Es (MPa)
    upper_angle_section: Dict[str, float]  # 상부앵글 단면 크기 (e.g., {'b': width, 't': thickness, ...})
    lower_angle_section: Dict[str, float]  # 하부앵글 단면 크기
    
    # L-form properties
    lform_fy: float  # L폼 Fy (MPa)
    lform_es: float  # L폼 Es (MPa)
    lform_section_properties: Dict[str, float]  # 단면계수, 2차모멘트, 도심 etc.

class TSCULDesign:
    """Main class for TSC UL type design program"""
    
    def __init__(self, inputs: DesignInputs):
        self.inputs = inputs
        self.results = {}  # To store results from each module
    
    def module1_input(self) -> DesignInputs:
        """Module 1: Handle input of design variables.
        In a full implementation, this would include user prompts or file reading.
        Returns: DesignInputs dataclass instance.
        """
        # Placeholder: Use provided inputs or implement input logic here
        print("Module 1: Design inputs loaded.")
        return self.inputs
    
    def module2_construction_load_check(self) -> Dict[str, Any]:
        """Module 2: Construction load structural strength calculation and comparison.
        As per PRD section 3.2 and user specs: Calculate DL/LL for y-dir (uniform, tributary y_span/(num_y_girders+1)),
        point loads P for x-dir at positions depending on num_y_girders (e.g., n=1: L/2; n=2: L/3, 2L/3; general: i*L/(n+1) for i=1 to n),
        then Mu/Vu for both directions based on support conditions.
        Compute bending and shear capacities (placeholder); compare.
        Assumes weld is safe.
        Returns: Dict with results for x and y directions.
        """
        print("Module 2: Performing construction load checks...")
        
        # y-dir girder loads (num_y_girders beams, tributary width = y_span / (num_y_girders + 1))
        tributary_width_y = self.inputs.x_span / (self.inputs.num_y_girders + 1)  # m
        dl_y = self.inputs.slab_thickness * self.inputs.concrete_density * tributary_width_y  # kN/m (uniform)
        ll_y = self.inputs.construction_live_load * tributary_width_y  # kN/m (uniform)
        
        w_y = 1.2*dl_y + 1.6*ll_y  # 1.2DL+1.6LL, total uniform load kN/m
        
        # y-dir girder DEMAND. uniform load, support-dependent
        l_y = self.inputs.y_span  # m

        if self.inputs.y_support_condition == 'pinned':
            y_result = pinned_pinned_uniform_load(w_y, l_y)
            mu_y = y_result['M_center']
            vu_y = y_result['R_A']

        elif self.inputs.y_support_condition == 'fixed':
            y_result = fixed_fixed_uniform_load(w_y, l_y)
            mu_y_pos = y_result['M_center'] #  moment kNm (중앙부, 정모멘트)
            vu_y = y_result['R_A']
            mu_y_neg = y_result['M_A']  # max moment kNm (양단부, 부모멘트), 값이 음수로 나옴
            mu_y = mu_y_pos # 일단은 정모멘트만 검토함
        else:
            raise ValueError("y_support_condition must be 'pinned' or 'fixed'")
        
        # x-dir girder loads: point loads from y-dir reactions at positions depending on num_y_girders
        # For general n = num_y_girders, positions = [i * L_x / (n + 1) for i in range(1, n+1)]
        # Each point load P = (w_y * y_span)  (end reaction per y-beam, assuming symmetric placement)
        # Note: Total point loads = n (one per y-beam, but actually 2 per beam; simplified to n effective symmetric points)
        # For n=1: position L/2, single P (or two at ends but central equiv.)
        # For n=2: positions L/3, 2L/3, two P's
        n = self.inputs.num_y_girders
        p = (w_y * self.inputs.y_span)  # kN per point load (상하부 y축 beam이 대칭으로 존재하기때문에. y_span 전체를 사용해야함.)
        l_x = self.inputs.x_span  # m

        if n == 1:
            pos = l_x / 2
            if self.inputs.x_support_condition == "pinned":
                x_result = pinned_pinned_point_load(p, pos, l_x)
                mu_x = x_result['M_F']
                vu_x = x_result['R_A']

            elif self.inputs.x_support_condition == "fixed":
                x_result = fixed_fixed_point_load(p, pos, l_x)
                mu_x_pos = x_result['M_F'] # moment kNm (중앙부, 정모멘트)
                vu_x = x_result['R_A']
                mu_x_neg = x_result['M_A'] # max moment kNm (양단부, 부모멘트), 값이 음수로 나옴
                mu_x = mu_x_pos # 일단은 정모멘트만 검토
            else:
                raise ValueError(f"Invalid support: {self.inputs.x_support_condition}")

        elif n == 2:
            pos1 = l_x / 3
            pos2 = 2 * l_x / 3
            if self.inputs.x_support_condition == "pinned":
                x_result1 = pinned_pinned_point_load(p, pos1, l_x)
                x_result2 = pinned_pinned_point_load(p, pos2, l_x)
                mu_x = x_result1['M_F'] + x_result2['M_F']
                vu_x = x_result1['R_A'] + x_result2['R_A']

            elif self.inputs.x_support_condition == "fixed":
                x_results = fixed_fixed_two_point_load(p, l_x)
                mu_x_pos = x_results['M_pos_max'] # moment kNm (중앙부, 정모멘트)
                vu_x = x_results['R_A']
                mu_x_neg = x_results['M_A'] # max moment kNm (양단부, 부모멘트), 값이 음수로 나옴
                mu_x = mu_x_pos # 일단은 정모멘트만 검토
            else:
                raise ValueError(f"Invalid support: {self.inputs.x_support_condition}")
        else:
            print(f"Warning: num_y_girders={n} >2; 코드를 수정하세요")
            mu_x = 0.0  # placeholder
            vu_x = 0.0
        
        # Placeholder capacities (to be implemented with angle/L-form sections)
        # e.g., mn_y = ... based on AISC for composite section
        capacity_mn_y = 0.0  # kNm
        capacity_vn_y = 0.0  # kN
        capacity_mn_x = 0.0  # kNm
        capacity_vn_x = 0.0  # kN
        
        positions = [l_x / 2] if n == 1 else [l_x / 3, 2 * l_x / 3]
        
        result = {
            # y-dir-beam
            'y_bending_ok': mu_y <= capacity_mn_y,
            'y_shear_ok': vu_y <= capacity_vn_y,
            'y_required_mu': mu_y,
            'y_capacity_mn': capacity_mn_y,
            'y_required_vu': vu_y,
            'y_capacity_vn': capacity_vn_y,
            # x-dir-girder
            'x_bending_ok': mu_x <= capacity_mn_x,
            'x_shear_ok': vu_x <= capacity_vn_x,
            'x_required_mu': mu_x,
            'x_capacity_mn': capacity_mn_x,
            'x_required_vu': vu_x,
            'x_capacity_vn': capacity_vn_x,
            # Loads summary
            'tributary_width_y': tributary_width_y,
            'w_y_dl': dl_y,
            'w_y_ll': ll_y,
            'w_y_total': w_y,
            'point_load_p': p,
            'num_y_girders': n,
            'x_point_positions': positions,
            'y_support_condition': self.inputs.y_support_condition,
            'x_support_condition': self.inputs.x_support_condition
        }
        self.results['module2'] = result
        return result
    
    def module3_formwork_pressure_check(self) -> Dict[str, Any]:
        """Module 3: Formwork lateral pressure strength calculation and comparison.
        As per PRD section 3.3: Calculate concrete lateral pressure, equivalent load w, Mu_form, Vu_form, deflection.
        Compute L-form capacities Mn, Vn, deflection limit (3mm); compare.
        Returns: Dict with {'bending_ok': bool, 'shear_ok': bool, 'deflection_ok': bool, ...}
        """
        print("Module 3: Performing formwork pressure checks...")
        # Placeholder
        # e.g., pressure = self.inputs.concrete_density * height * g
        result = {
            'bending_ok': True,
            'shear_ok': True,
            'deflection_ok': True,
            'max_mu': 0.0,
            'mn': 0.0,
            'max_vu': 0.0,
            'vn': 0.0,
            'max_delta': 0.0,
            'allow_delta': 3.0  # mm
        }
        self.results['module3'] = result
        return result
    
    def module4_weld_strength_check(self) -> Dict[str, Any]:
        """Module 4: Weld strength calculation and review.
        As per PRD section 3.4: Study weld strength, calculate demand from modules 2/3, capacity, compare.
        Determine required weld length/thickness.
        Returns: Dict with {'weld_ok': bool, 'required_length': float, ...}
        """
        print("Module 4: Performing weld strength checks...")
        # Placeholder: Use demands from previous modules
        result = {
            'weld_ok': True,
            'required_weld_length': 0.0,  # mm
            'weld_capacity': 0.0
        }
        self.results['module4'] = result
        return result
    
    def module5_generate_report(self) -> None:
        """Module 5: Report writing and visualization.
        As per PRD section 3.5: Compile results, generate report (e.g., PDF/Markdown), plots.
        """
        print("Module 5: Generating report...")
        # Placeholder: Print summary or save to file
        summary = f"""
TSC UL Design Report Summary:
- Inputs: {self.inputs}
- Module 2: {self.results.get('module2', {})}
- Module 3: {self.results.get('module3', {})}
- Module 4: {self.results.get('module4', {})}
        """
        print(summary)
        
        # Example visualization
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Placeholder Plot\n(Results Visualization)', ha='center', va='center')
        ax.set_title('TSC UL Design Results')
        plt.savefig('/Users/peter/Projects/tsc-ul-structural-check/report_plot.png')
        plt.close()
        print("Report plot saved as report_plot.png")
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run all modules in sequence."""
        self.module1_input()
        self.module2_construction_load_check()
        self.module3_formwork_pressure_check()
        self.module4_weld_strength_check()
        self.module5_generate_report()
        return self.results

# Example usage
if __name__ == "__main__":
    # Example inputs (to be replaced with actual input method)
    example_inputs = DesignInputs(
        x_span=10.8,
        y_span=10.2,
        slab_thickness=0.2,
        construction_live_load=2.5,
        concrete_density=24.0,
        num_y_girders=2,
        x_support_condition='fixed',
        y_support_condition='pinned',
        angle_fy=235.0,
        angle_es=200000.0,
        upper_angle_section={'b': 100, 't': 10},  # mm
        lower_angle_section={'b': 100, 't': 10},
        lform_fy=235.0,
        lform_es=200000.0,
        lform_section_properties={'I': 1e6, 'S': 1e4, 'e': 0.0}  # Placeholder units
    )
    
    design = TSCULDesign(example_inputs)
    results = design.run_full_analysis()
    print("Analysis complete. Results:", results)   