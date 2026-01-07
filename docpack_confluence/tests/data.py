# -*- coding: utf-8 -*-

# Title format: {type}{seq:02d}-L{level}
# e.g., p01-L1, f04-L4, p77-L12
hierarchy_specs = [
    # ══════════════════════════════════════════════════════════════════
    # Branch 1: p01 → deep path to L12, with clustering at L4-L5, L8-L9
    # ══════════════════════════════════════════════════════════════════
    "p01-L1",
    "p01-L1/p02-L2",
    "p01-L1/p02-L2/p03-L3",
    # --- f04: clustering parent at L4 (6 children at L5) ---
    "p01-L1/p02-L2/p03-L3/f04-L4",  # [clustering parent]
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5",  # (continues deep)
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6",
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7",
    # --- f08: clustering parent at L8 (4 children at L9) ---
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8",  # [clustering parent]
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/p09-L9",  # (continues deep)
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/p09-L9/p10-L10",
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/p09-L9/p10-L10/p11-L11",
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/p09-L9/p10-L10/p11-L11/p12-L12",  # ★
    # f08's other L9 children (siblings of p09)
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/p13-L9",
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/f14-L9",
    "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5/p06-L6/p07-L7/f08-L8/f15-L9",
    # f04's other L5 children (siblings of p05)
    "p01-L1/p02-L2/p03-L3/f04-L4/p16-L5",
    "p01-L1/p02-L2/p03-L3/f04-L4/f17-L5",
    "p01-L1/p02-L2/p03-L3/f04-L4/p18-L5",
    "p01-L1/p02-L2/p03-L3/f04-L4/f19-L5",
    "p01-L1/p02-L2/p03-L3/f04-L4/p20-L5",
    # --- f21: clustering parent at L4 (5 children at L5) ---
    "p01-L1/p02-L2/p03-L3/f21-L4",  # [clustering parent]
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5",  # (continues deep)
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6",
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7",
    # --- f25: clustering parent at L8 (4 children at L9) ---
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8",  # [clustering parent]
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/p26-L9",  # (continues deep)
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/p26-L9/f27-L10",
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/p26-L9/f27-L10/p28-L11",
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/p26-L9/f27-L10/p28-L11/f29-L12",  # ★
    # f25's other L9 children (siblings of p26)
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/f30-L9",
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/p31-L9",
    "p01-L1/p02-L2/p03-L3/f21-L4/p22-L5/f23-L6/p24-L7/f25-L8/f32-L9",
    # f21's other L5 children (siblings of p22)
    "p01-L1/p02-L2/p03-L3/f21-L4/f33-L5",
    "p01-L1/p02-L2/p03-L3/f21-L4/p34-L5",
    "p01-L1/p02-L2/p03-L3/f21-L4/f35-L5",
    "p01-L1/p02-L2/p03-L3/f21-L4/p36-L5",
    # p03's other child at L3
    "p01-L1/p02-L2/f37-L3",
    # --- p38: clustering parent at L4 (6 children at L5) ---
    "p01-L1/p02-L2/f37-L3/p38-L4",  # [clustering parent]
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5",  # (continues deep)
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6",
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7",
    # --- p42: clustering parent at L8 (4 children at L9) ---
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8",  # [clustering parent]
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/f43-L9",  # (continues deep)
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/f43-L9/p44-L10",
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/f43-L9/p44-L10/f45-L11",
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/f43-L9/p44-L10/f45-L11/p46-L12",  # ★
    # p42's other L9 children (siblings of f43)
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/p47-L9",
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/f48-L9",
    "p01-L1/p02-L2/f37-L3/p38-L4/p39-L5/f40-L6/p41-L7/p42-L8/p49-L9",
    # p38's other L5 children (siblings of p39)
    "p01-L1/p02-L2/f37-L3/p38-L4/f50-L5",
    "p01-L1/p02-L2/f37-L3/p38-L4/p51-L5",
    "p01-L1/p02-L2/f37-L3/p38-L4/f52-L5",
    "p01-L1/p02-L2/f37-L3/p38-L4/p53-L5",
    "p01-L1/p02-L2/f37-L3/p38-L4/f54-L5",
    # p01's other child at L2
    "p01-L1/f55-L2",
    # ══════════════════════════════════════════════════════════════════
    # Branch 2: p01/f55 → single chain to L12
    # ══════════════════════════════════════════════════════════════════
    "p01-L1/f55-L2/p56-L3",
    "p01-L1/f55-L2/p56-L3/f57-L4",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6/p60-L7",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6/p60-L7/f61-L8",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6/p60-L7/f61-L8/p62-L9",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6/p60-L7/f61-L8/p62-L9/f63-L10",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6/p60-L7/f61-L8/p62-L9/f63-L10/p64-L11",
    "p01-L1/f55-L2/p56-L3/f57-L4/p58-L5/f59-L6/p60-L7/f61-L8/p62-L9/f63-L10/p64-L11/f65-L12",  # ★
    # ══════════════════════════════════════════════════════════════════
    # Branch 3: f66 → single chain to L12
    # ══════════════════════════════════════════════════════════════════
    "f66-L1",
    "f66-L1/p67-L2",
    "f66-L1/p67-L2/f68-L3",
    "f66-L1/p67-L2/f68-L3/p69-L4",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6/f72-L7",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6/f72-L7/p73-L8",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6/f72-L7/p73-L8/f74-L9",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6/f72-L7/p73-L8/f74-L9/p75-L10",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6/f72-L7/p73-L8/f74-L9/p75-L10/f76-L11",
    "f66-L1/p67-L2/f68-L3/p69-L4/f70-L5/p71-L6/f72-L7/p73-L8/f74-L9/p75-L10/f76-L11/p77-L12",  # ★
]
