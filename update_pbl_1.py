import re

def main():
    file_path = "sepora_rbt_toolkit.html"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Dropdown Tahun 4
    dropdown_4 = """<select id="selectPblTahun4" class="form-select" onchange="handleDropdownTahunChange('4', this.value)" style="border-color: #fbcfe8; font-weight: 600; font-size: 0.85rem;">
                    <option value="" disabled selected>-- Pilih Mengikut Unit (Tahun 4) --</option>
                    <option value="4_kereta_idamanku">PBL 1: REKA BENTUK "KERETA IDAMANKU" (Unit 2)</option>
                    <option value="4_pen3d">PBL 2: PENGENALAN KEPADA TEKNOLOGI KEYCHAIN 3D PEN (Unit 3)</option>
                    <option value="4_jahitan">PBL 3: PENGENALAN KEPADA TEKNOLOGI JAHITAN (Unit 3)</option>
                    <option value="4_pembungkusan">PBL 4: REKA BENTUK PEMBUNGKUSAN (Unit 4)</option>
                    <option value="4_makanan">PBL 5: REKA BENTUK MAKANAN (Unit 5)</option>
                    <option value="4_pengaturcaraan">PBL 6: REKA BENTUK PENGATURCARAAN (Unit 6)</option>
                  </select>"""
    content = re.sub(r'<select id="selectPblTahun4".*?</select>', dropdown_4, content, flags=re.DOTALL)

    # 2. Update Dropdown Tahun 5
    dropdown_5 = """<select id="selectPblTahun5" class="form-select" onchange="handleDropdownTahunChange('5', this.value)" style="border-color: #bfdbfe; font-weight: 600; font-size: 0.85rem;">
                    <option value="" disabled selected>-- Pilih Mengikut Unit (Tahun 5) --</option>
                    <option value="5_rumah_tangga">PBL 1: TEKNOLOGI RUMAH TANGGA ARTIKEL JAHITAN (Unit 1)</option>
                    <option value="5_kipas_solar">PBL 2: TABUNG KIPAS SOLAR (Unit 2)</option>
                    <option value="5_atmega">PBL 3: PENGATURCARAAN KIT ATMEGA328P (Unit 3)</option>
                    <option value="5_tanaman">PBL 4: Tanaman Konvensional (Unit 4)</option>
                  </select>"""
    content = re.sub(r'<select id="selectPblTahun5".*?</select>', dropdown_5, content, flags=re.DOTALL)

    # 3. Update Dropdown Tahun 6
    dropdown_6 = """<select id="selectPblTahun6" class="form-select" onchange="handleDropdownTahunChange('6', this.value)" style="border-color: #e9d5ff; font-weight: 600; font-size: 0.85rem;">
                    <option value="" disabled selected>-- Pilih Mengikut Unit (Tahun 6) --</option>
                    <option value="6_kereta_kawalan">PBL 1: KERETA KAWALAN SAYA (Unit 1)</option>
                    <option value="6_auto_plant">PBL 2: Auto Plant Watering (Unit 2)</option>
                    <option value="6_penghasilan">PBL 3: Penghasilan Produk (Unit 3)</option>
                  </select>"""
    content = re.sub(r'<select id="selectPblTahun6".*?</select>', dropdown_6, content, flags=re.DOTALL)

    # 4. Update the badges that say "UNIT 1 - 4" for T4, T5, T6
    # For T4: UNIT 2 - 6
    content = re.sub(r'<span class="badge" style="background:#fce7f3; color:#be185d; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">UNIT 1 - 4</span>',
                     '<span class="badge" style="background:#fce7f3; color:#be185d; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">UNIT 2 - 6</span>', content)
    # For T5: UNIT 1 - 4
    content = re.sub(r'<span class="badge" style="background:#dbeafe; color:#1d4ed8; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">UNIT 1 - 4</span>',
                     '<span class="badge" style="background:#dbeafe; color:#1d4ed8; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">UNIT 1 - 4</span>', content)
    # For T6: UNIT 1 - 3
    content = re.sub(r'<span class="badge" style="background:#f3e8ff; color:#7e22ce; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">UNIT 1 - 4</span>',
                     '<span class="badge" style="background:#f3e8ff; color:#7e22ce; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">UNIT 1 - 3</span>', content)

    # 5. Update the "Susunan Mengikut Unit" buttons
    buttons_html = """<div style="background:var(--bg); border:1px solid var(--surface-border); border-radius:8px; padding:0.6rem 0.85rem; margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
              <span style="font-size:0.8rem; font-weight:700; color:var(--text);"><i class="fa-solid fa-arrow-down-1-9" style="color:var(--primary);"></i> Akses Pantas:</span>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('4_kereta_idamanku')" style="background:#fce7f3; color:#be185d; border:1px solid #f472b6; font-size:0.75rem;">T4 U2: Kereta</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('4_pen3d')" style="background:#e0f2fe; color:#0369a1; border:1px solid #38bdf8; font-size:0.75rem;">T4 U3: Pen 3D</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('4_jahitan')" style="background:#fdf2f8; color:#9d174d; border:1px solid #fbcfe8; font-size:0.75rem;">T4 U3: Jahitan</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('4_pembungkusan')" style="background:#dcfce7; color:#15803d; border:1px solid #4ade80; font-size:0.75rem;">T4 U4: Bungkus</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('4_makanan')" style="background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-size:0.75rem;">T4 U5: Makanan</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('4_pengaturcaraan')" style="background:#ede9fe; color:#6b21a8; border:1px solid #ddd6fe; font-size:0.75rem;">T4 U6: Scratch</button>
              
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('5_rumah_tangga')" style="background:#ede9fe; color:#6b21a8; border:1px solid #ddd6fe; font-size:0.75rem;">T5 U1: R.Tangga</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('5_kipas_solar')" style="background:#fef3c7; color:#92400e; border:1px solid #fcd34d; font-size:0.75rem;">T5 U2: Kipas Solar</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('5_atmega')" style="background:#dbeafe; color:#1d4ed8; border:1px solid #60a5fa; font-size:0.75rem;">T5 U3: ATMEGA</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('5_tanaman')" style="background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe; font-size:0.75rem;">T5 U4: Tanaman</button>
              
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('6_kereta_kawalan')" style="background:#faf5ff; color:#6b21a8; border:1px solid #e9d5ff; font-size:0.75rem;">T6 U1: Kereta K</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('6_auto_plant')" style="background:#e0e7ff; color:#3730a3; border:1px solid #c7d2fe; font-size:0.75rem;">T6 U2: Auto Plant</button>
              <button type="button" class="btn btn-sm" onclick="loadPblRbtTemplate('6_penghasilan')" style="background:#f3e8ff; color:#7e22ce; border:1px solid #c084fc; font-size:0.75rem;">T6 U3: Produk</button>
            </div>"""
    content = re.sub(r'<div style="background:var\(--bg\); border:1px solid var\(--surface-border\).*?</div>\s*</div>\s*<div style="display:grid;', buttons_html + '\n\n            <div style="display:grid;', content, flags=re.DOTALL)

    # 6. Replace formRphTahap dropdown options
    form_tahap = """<select id="formRphTahap" class="form-select" onchange="loadPblRbtTemplate(this.value)">
                  <optgroup label="Tahun 4">
                    <option value="4_kereta_idamanku">PBL 1: REKA BENTUK "KERETA IDAMANKU" (Unit 2)</option>
                    <option value="4_pen3d">PBL 2: PENGENALAN KEPADA TEKNOLOGI KEYCHAIN 3D PEN (Unit 3)</option>
                    <option value="4_jahitan">PBL 3: PENGENALAN KEPADA TEKNOLOGI JAHITAN (Unit 3)</option>
                    <option value="4_pembungkusan">PBL 4: REKA BENTUK PEMBUNGKUSAN (Unit 4)</option>
                    <option value="4_makanan">PBL 5: REKA BENTUK MAKANAN (Unit 5)</option>
                    <option value="4_pengaturcaraan">PBL 6: REKA BENTUK PENGATURCARAAN (Unit 6)</option>
                  </optgroup>
                  <optgroup label="Tahun 5">
                    <option value="5_rumah_tangga">PBL 1: TEKNOLOGI RUMAH TANGGA ARTIKEL JAHITAN (Unit 1)</option>
                    <option value="5_kipas_solar">PBL 2: TABUNG KIPAS SOLAR (Unit 2)</option>
                    <option value="5_atmega">PBL 3: PENGATURCARAAN KIT ATMEGA328P (Unit 3)</option>
                    <option value="5_tanaman">PBL 4: Tanaman Konvensional (Unit 4)</option>
                  </optgroup>
                  <optgroup label="Tahun 6">
                    <option value="6_kereta_kawalan">PBL 1: KERETA KAWALAN SAYA (Unit 1)</option>
                    <option value="6_auto_plant">PBL 2: Auto Plant Watering (Unit 2)</option>
                    <option value="6_penghasilan">PBL 3: Penghasilan Produk (Unit 3)</option>
                  </optgroup>
                </select>"""
    content = re.sub(r'<select id="formRphTahap".*?</select>', form_tahap, content, flags=re.DOTALL)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
if __name__ == "__main__":
    main()
