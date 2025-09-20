from pathlib import Path
BASE = Path(__file__).resolve().parents[1] / "app" / "models" / "data"
BASE.mkdir(parents=True, exist_ok=True)

def write(name: str, text: str):
    (BASE / name).write_text(text.strip() + "\n", encoding="utf-8")

write("projects.csv", """project_id,name,category,goal_amount,deadline,raised_amount
12345678,AI For Schools,Education,100000,2030-01-01,25000
12345679,Green Farm,Environment,80000,2030-02-01,10000
12345680,Robotics Club,Education,120000,2030-03-01,50000
12345681,Health App,Health,150000,2030-04-01,30000
12345682,Open Library,Community,60000,2030-05-01,20000
12345683,Music Studio,Arts,70000,2030-06-01,15000
12345684,STEM Kit,Education,90000,2030-07-01,40000
12345685,Recycling Hub,Environment,110000,2030-08-01,35000
""")

write("reward_tiers.csv", """project_id,tier_id,name,min_amount,quota
12345678,T1,Sticker Pack,200,50
12345678,T2,T-Shirt,600,30
12345679,T1,Seed Set,300,40
12345679,T2,Workshop Pass,700,20
12345680,T1,Robot Pin,250,60
12345680,T2,Lab Tour,800,25
12345681,T1,Health Badge,200,50
12345681,T2,Premium Access,1000,10
12345682,T1,Donor Wall,300,40
12345682,T2,Founder Badge,900,15
12345683,T1,Digital Album,150,70
12345683,T2,Studio Visit,900,10
12345684,T1,STEM Sticker,150,70
12345684,T2,Prototype Demo,1000,10
12345685,T1,Recycling Badge,200,50
12345685,T2,Volunteer Kit,700,20
""")

write("users.csv", """user_id,username,password,display_name
U01,alice,alice123,Alice
U02,bob,bob123,Bob
U03,charlie,charlie123,Charlie
U04,david,david123,David
U05,eve,eve123,Eve
U06,frank,frank123,Frank
U07,grace,grace123,Grace
U08,heidi,heidi123,Heidi
U09,ivan,ivan123,Ivan
U10,judy,judy123,Judy
U11,kevin,kevin123,Kevin
""")

write("pledges.csv", "pledge_id,user_id,project_id,created_at,amount,tier_id,status,reject_reason")
print(f"Seeded CSV into {BASE}")
