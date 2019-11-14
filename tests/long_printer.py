'''
This is is a very basic stdio handler script. This is used by python.py example.
'''

import time

puskas_wiki = ['''Ferenc Puskas was a Hungarian footballer and manager, widely regarded as one of \
the greatest players of all time. He is the son of former footballer Ferenc Puskas Senior. A \
prolific forward, he scored 84 goals in 85 international matches for Hungary, played 4 \
international matches for Spain and scored 514 goals in 529 matches in the Hungarian and Spanish \
leagues. He became an Olympic champion in 1952 and led his nation to the final of the 1954 World \
Cup where he was named the tournament's best player. He won three European Cups (1959, 1960, 1966),\
 10 national championships (5 Hungarian and 5 Spanish Primera Division) and 8 top individual \
 scoring honors. In 1995, he was recognized as the top scorer of the 20th century by the IFFHS.''',
'''Puskas started his career in Hungary playing for Kispest and Budapest Honved. He was the top scorer\
 in the Hungarian League on four occasions, and in 1948, he was the top goal scorer in Europe. \
 During the 1950s, he was both a prominent member and captain of the Hungarian national team, known\
 as the Mighty Magyars. In 1958, two years after the Hungarian Revolution, he emigrated to Spain \
 where he played for Real Madrid. While playing with Real Madrid, Puskas won four Pichichis and \
 scored seven goals in two European Champions Cup finals.''',
'''After retiring as a player, he became a coach. The highlight of his coaching career came in 1971 \
when he guided Panathinaikos to the European Cup final, where they lost 2-0 to AFC Ajax. In 1993, \
he returned to Hungary and took temporary charge of the Hungarian national team. In 1998, he \
became one of the first ever FIFA/SOS Charity ambassadors. In 2002, the Nepstadion in Budapest \
was renamed the Puskas Ferenc Stadion in his honor. He was also declared the best Hungarian \
player of the last 50 years by the Hungarian Football Federation in the UEFA Jubilee Awards in \
November 2003. In October 2009, FIFA announced the introduction of the FIFA Puskas Award, \
awarded to the player who has scored the "most beautiful goal" over the past year. He was also \
listed in Pele's FIFA 100.''',
 '''Ferenc Purczeld was born on 2 April 1927 to a German (Danube Swabian) family in Budapest and \
brought up in Kispest, then a suburb, today part of the city. His mother, Margit Biro \
(1904-1976), was a seamstress. He began his career as a junior with Kispest AC,[10] where his \
father, who had previously played for the club, was a coach. He had grandchildren, who were the \
children of his brothers son[clarification needed]; the two sons of his brother are Zoltan and \
Istvan, the first one have 3 children; Ilonka, Camila and Andres, and the second one have two.''', 
'''He changed his name to Puskas. He initially used the pseudonym "Miklos Kovacs" to help \
circumvent the minimum age rules[12] before officially signing at the age of 12. Among his early \
teammates was his childhood friend and future international teammate Jozsef Bozsik. He made his \
first senior appearance for Kispest in November 1943 in a match against Nagyvaradi AC.[13] It was \
here where he got the nickname "Ocsi" or "Buddy".[14]''', 
'''Kispest was taken over by the Hungarian Ministry of Defence in 1949, becoming the Hungarian Army \
team and changing its name to Budapest Honved. As a result, football players were given military \
ranks. Puskas eventually became a major (Hungarian: Ornagy), which led to the nickname "The \
Galloping Major".[15] As the army club, Honved used conscription to acquire the best Hungarian \
players, leading to the recruitment of Zoltan Czibor and Sandor Kocsis.[16] During his career at \
Budapest Honved, Puskas helped the club win five Hungarian League titles. He also finished as top \
goal scorer in the league in 1947-48, 1949-50, 1950 and 1953, scoring 50, 31, 25 and 27 goals, \
respectively. In 1948, he was the top goal scorer in Europe.[17]''' ] 

def main():
    print('Welcome!')

    while True:
        print('puskas> ', end='')
        num = input()
        
        if num == 'exit':
            break
        if num == 'all':
            print('\r\n'.join(puskas_wiki))
            continue
        try:
            if int(num) in range(len(puskas_wiki)):
                print(puskas_wiki[int(num)])
                continue
        except:
            pass
        print('unknown command')

if __name__ == '__main__':
    main()
    