from django.core.exceptions import ValidationError
from django.contrib.auth import (
    login, get_user_model, authenticate,
)
from disposable_email_domains import blocklist
import re

User = get_user_model()

simplest_passwords = ['abc123', '1qaz2wsx', '123qwe', 'trustno1', 'poop99', '1234qwer', 'q1w2e3r4t5', 'qwer1234', 'ncc1701', 'q1w2e3r4', '1q2w3e4r', 'thx1138', 'jordan23', '123abc', '123456a', 'abcd1234', 'password1', 'qwerty123', '1q2w3e4r5t', 'q1w2e3', '123456q', 'bond007', '12345a', 'rush2112', 'red123', 'passw0rd', '1qazxsw2', 'blink182', '12qwaszx', 'asdf1234', 'lol123', 'asd123', 'ou812', 'qwerty1', '12345q', 'hello1', '1232323q', 'eagle1', '12345qwert', 'qwe123', 'lucky1', 'a12345', '123456789a', 'a123456', 'Usuckballz1', 'qwerty12', 'zaq12wsx', 'money1', 'rasdzv3', '123123a', 'test123', 'ncc1701d', 'hello123', '1q2w3e', 'happy1', 'michael1', 'qqq111', 'a1b2c3', '123456789q', 'zxc123', 'qaz123', 'alpha1', 'bubba1', 'catch22', '123qweasd', 'tiger1', 'charlie1', 'a1b2c3d4', 'password123', 'buddy1', 'angel1', 'Soso123aljg', 'chris1', '123qweasdzxc', 'letmein1', 'pussy1', 'oicu812', 'james1', '1234abcd', 'qazwsx123', 'mustang1', 'rocky1', 'freedom1', 'fuckyou2', '1a2b3c', '1qaz2wsx3edc', 'dragon1', 'monkey1', 'welcome1', '123qwe123', 'wrinkle1', 'q12345', 'access14', '123asd', 'babylon5', 'david1', 'yankees1', 'q1w2e3r4t5y6', 'jessica1', 'sammy1', 'sex4me', 'jesus1', 'ncc1701e', 'super123', 'blue22', 'apple1', 'letmein2', 'a1234567', '1q1q1q', 'gn56gn56', 'matthew1', 'shadow1', 'molly1', 'anthony1', 'satan666', 'zaq123', 'colt45', '1q2w3e4r5t6y', 'master1', 'fuckyou1', 'seven7', 'shaney14', 'qwerty12345', 'magic1', '1234567a', 'pepsi1', 'jason1', 'blue123', 'green1', 'asdf123', '123456z', 'lucky7', '1a2b3c4d', 'Mailcreated5240', 'woody1', 'test1', '123qaz', 'pass123', 'black1', 'william1', '123zxc', '1234567q', 'viper1', 'honda1', 'zaq1xsw2', 'pussy69', 'abc12', 'zxcv1234', 'formula1', 'a1s2d3f4', '123321q', 'thunder1', 'heather1', 'chelsea1', '123456qwerty', 'sasha1', '1234567890q', 'rusty1', 'q1q1q1', 'Passw0rd', 'area51', '8J4yE3Uz', 'sarah1', 'richard1', 'john316', 'usa123', 'qwerty123456', 'power1', 'oscar1', 'asshole1', 'amber1', 'aaa111', 'frank1', 'qwert123', 'andrew1', 'scooter1', 'kevin1', 'elvis1', 'delta1', 'soccer1', 'ncc1701a', 'pa55word', 'patrick1', 'gateway1', 'cowboys1', 'homer1', 'agent007', 'porsche9', '123456k', 'star69', 'omega1', 'gizmo1', 'ranger1', 'diamond1', 'Password1', 'hunter1', 'horny1', '1qaz1qaz', '1234qwe', 'pokemon1', 'super1', 'robert1', 'jimmy1', '123456789z', 'Turkey50', 'front242', 'apollo13', 'gordon24', 'brandon1', 'casey1', '4runner', 'raven1', 'arsenal1', 'br0d3r', '123456aa', 'raiders1', 'daddy1', '1Passwor', 'tyler1', 'Sojdlg123aljg', 'jackson1', 'bitch1', 'thomas1', 'steve1', 'kitty1', 'killer1', 'fordf150', 'cloud9', 'kelly1', 'harley1', 'texas1', 'pa55w0rd', 'number1', 'daisy1', 'billy1', '50cent', 'melissa1', 'kcj9wx5n', 'happy123', 'football1', 'crazy1', 'abc12345', 'chevy1', '1qa2ws3ed', 'rangers1', 'p0015123', 'nwo4life', 'lucky13', 'jenny1', 'irish1', 'emily1', '123123q', 'phoenix1', 'hal9000', 'qwer123', 'music1', 'katie1', 'pass1234', 'xbox360', 'ne1469', 'love69', 'jordan1', 'daniel1', 'chester1', 'batman1', '123456r', 'z1x2c3', 'vh5150', 'sandy1', 'jasmine1', 'buster1', 'sex123', 'r2d2c3po', 'chicken1', 'bob123', 'summer1', 'snake1', 'route66', 'q123456', 'Passwor1', 'marino13', 'bobby1', 'apple123', '12345z', 'wolf359', 'tommy1', 'samsung1', 'peter1', 'love123', '1x2zkg8w', 'test1234', 'sexy69', 'sadie1', 'qwert1', 'fucku2', 'flash1', 'a123456789', 'secret1', 'audia4', 'america1', '12345678q', 'qazwsx12', 'holly1', 'moose1', 'qwerty1234', 'montgom240', 'cat123', '12qw34er', '123qwerty', '123aaa', 'abc1234', '1q2w3e4r5', 'superman1', 'ou8122', 'joker1', 'cbr600', 'amanda1', 'a1s2d3', 'turbo1', 'spike1', 'pepper1', 'great1', 'zxcvbnm1', 'james007', '12345qwe', 'zxasqw12', 'xxx123', 'gfhjkm123', 'enter1', 'cobra1', '123456s', 'Pussy1', 'jacob1', 'death1', 'honey1', 'packers1', 'newpass6', 'mouse1', 'justin1', 'charles1', '12qwas', 'gsxr750', 'dodge1', 'cheese1', '12345678a', 'shannon1', 'madison1', 'a1a1a1', 'simon1', 'PolniyPizdec0211', 'nokia6300', 'misty1', 'logan1', 'harry1', 'chicago1', 'bunny1', 'abcd123', '12qw12', 'br549', '7uGd5HIp2J', '1qaz2ws', '123321a', 'penny1', 'max123', 'maria1', 'just4me', 'jamie1', 'florida1', 'buffy1', 'brian1', 'baseball1', 'adam12', 'love12', 'ib6ub9', 'ABC123', '123qq123', '12345t', '1234567890a', 'xyz123', 'nasty1', 'missy1', 'bella1', 'ashley1', '50spanks', 'sweet1', 'password2', 'orange1', 'gfhjkm1', 'digital1', '123456qw', 'z1x2c3v4', 'vSjasnel12', 'q2w3e4r5', 'nicole1', 'lineage2', 'fuckoff1', 'temp123', 'qazwsx1', 'newyork1', 'fishing1', 'dragon12', 'dog123', 'a11111', 'wg8e3wjf', 'teddy1', 'rebecca1', 'mikey1', 'ferrari1', 'eagles1', '111111a', 'monster1', 'martin1', 'crystal1', 'bingo1', 'alex123', 'winston1', 'orion1', 'monkey12', 'jackson5', 'ginger1', 'george1', 'gator1', '1234asdf', 'sassy1', 'rachel1', 'panther1', 'green123', 'danny1', 'bird33', '1z2x3c', '1a2s3d4f', '123456qwe', 'spurs1', 'slave1', 'sam123', 'linda1', 'gandalf1', 'devil666', 'bruno1', '9293709b13', '1qa2ws', '1Pussy', 'tigger1', 'sally1', 'rainbow6', 'qazwsxedc123', 'hockey1', 'chloe1', 'bubba69', '111qqq', 'scorpio1', 'rebel1', 'q1q2q3', 'ninja1', 'marine1', 'lover1', 'karen1', 'iverson3', 'guitar1', 'carmex2', 'blue12', '123qw', 'silver1', 'scott1', 'qwer12', 'bulldog1', 'aaron1', '426hemi', '111111q', 'taylor1', 'Michael1', 'master12', 'joshua1', 'icu812', 'Good123654', 'ghost1', 'dolphin1', 'asdf12', 'a1a2a3', 'a12345678', 'tigger2', 'super12', 'pussy123', 'morgan1', 'henry1', '1234qw', '123456l', 'tiger123', 'summer99', 'playboy1', 'oliver1', 'michael2', 'mandy1', 'killer12', 'julie1', 'iloveyou2', 'dusty1', 'annie1', '81fukkc', 'zxcvbnm123', 'Stone55', 'pool6123', 'mazdarx7', 'mason1', 'mama123', 'hawaii50', 'gabriel1', 'edward1', 'cindy1', '45M2DO5BS', '1z2x3c4v', '123456m', 'yankees2', 'tiffany1', 'qwerty7', 'nikki1', 'nascar24', 'mickey1', 'mazda626', 'bmw325', 'asdfgh01', '123456789s', 'water1', 'tiger2', 'sparky1', 'snoopy1', 'redsox1', 'porno1', 'mike123', 'Master1', 'maggie1', 'just4fun', 'dallas1', 'cameron1', 'andyod22', '123ewq', 'sexy1', 'pizza1', 'password12', 'larry1', 'james123', 'eddie1', 'drummer1', 'Dragon1', 'chase1', 'sheba1', 'qwerty11', 'qweasd123', 'jimbo1', 'felix1', 'broncos1', 'zxcasdqwe123', 'soccer12', 'soccer10', 'slick1', 'qwert12345', 'pumpkin1', 'porsche1', 'noname123', 'megan1', 'joe123', 'jerry1', 'hannah1', 'death666', 'bailey1', 'austin1', '3000gt', '12qw12qw', 'sf49ers', 'mazda6', 'laura1', 'Kordell1', 'house1', 'angel123', '3x7PxR', '12345qw', '123456ru', 'WP2003WP', 'smoke1', 'simba1', 'pufunga7782', 'iloveyou1', 'fuck123', 'david123', 'cookie1', 'Beast1', '57chevy', 'yamahar1', 'sugar1', 'spencer1', 'smokey1', 'q11111', 'mother1', 'marcius2', 'junior1', 'ghbdtn123', 'cygnusx1', 'casper1', 'buddy123', 'bruce1', '12345s', '11111q', 'zachary1', 'test12', 'rusty2', 'qwert40', 'qwe123qwe', 'nancy1', 'mustang6', 'monty1', 'Misfit99', 'Letmein1', 'jackass1', 'heidi1', 'ghhh47hj7649', 'diablo2', 'blue32', '1qwerty', '1234zxcv', 'white1', 'vikings1', 'Qwerty1', 'q2w3e4', 'pinky1', 'penguin1', 'Password123', 'money12', 'mario1', 'love1', 'jones1', 'john123', 'candy1', '1a2s3d', '12345qwerty', 'sunny1', 'shadow12', 'private1', 'nokian73', 'hallo123', 'cbr900rr', 'asdqwe123', '4ever', 'wendy1', 'warrior1', 'vader1', 'Trustno1', 'storm1', 'qqqqq1', 'nirvana1', 'money123', 'max333', 'marines1', 'little1', 'happy2', 'golfer1', 'elway7', 'dylan1', 'cricket1', 'chris123', 'bubba123', 'blues1', 'april1', 'andrea1', 'a1234', '1qaz', '123qwer', 'Welcome1', 'paris1', 'ou8123', 'loser1', 'fender1', 'falcon1', 'f00tball', 'cafc91', 'brown1', '159357a', 'weed420', 'start1', 'qwe321', 'peaches1', 'peace1', 'nokia6233', 'merlin1', 'maxwell1', 'mash4077', 'hello12', 'fuck69', 'dirty1', 'cowboy1', 'zxcv123', 'spider1', 'spartan1', 'roger1', 'q123456789', 'power123', 'magic32', 'genesis1', 'favorite6', 'dodgers1', 'brandy1', 'blue99', 'awesome1', 'all4one', '2fast4u', '12345qaz', 'tyson1', 'trouble1', 'tigers1', 'testing1', 'summer69', 'segblue2', 'randy1', 'p0o9i8u7', 'lakers1', 'joseph1', 'gsxr1000', 'flower2', 'blue42', 'austin31', 'alice1', '5Wr2i7H8', '3ip76k2', '23skidoo', '1Dragon', '123qwert', '12345qwer', '12345abc', '123456t', '123456789m', 'winter1', 'voyager1', 'sixty9', 'scuba1', 'sammy123', 'rainbow1', 'perfect1', 'pantera1', 'p4ssw0rd', 'nathan1', 'm123456', 'Jordan23', 'johnson1', 'holein1', 'dragon69', 'compaq1', 'boomer1', 'blue1234', 'barry1', 'angus1', 'alex12', '1q2q3q', '12345m', '123456789qwe', '11111a', 'smart1', 'sabrina1', 'q1234567', 'poker1', 'nokia1', 'ncc74656', 'natasha1', 'met2002', 'hello2', 'faith1', 'doggy1', 'destiny1', 'dakota1', 'asd222', '1qazzaq1', '1qazxsw23edc', '123456qqq', '123456789d', '007bond', 'stone1', 'stephen1', 'slayer1', 'robin1', 'q1w2e3r', 'panda1', 'Mustang1', 'liverpool1', 'killer123', 'jeter2', 'jeremy1', 'gonzo1', 'golden1', 'frodo1', 'chaos1', 'buffalo1', '7777777a', '1passwor', '123456n', 'young1', 'winner1', 'therock1', 'tanya1', 'success1', 'stupid1', 'sex69', 's123456', 'password9', 'miller1', 'marie1', 'johnny5', 'fuckme2', 'eclipse1', 'charlie2', '49ers', '1qw23er4', '1q1q1q1q', '1Master', '1234rewq', '12345r', '101091m', 'wizard1', 'weare138', 'vanessa1', 'tasha1', 'rugby1', 'purple1', 'prince1', 'patches1', 'password99', 'matrix1', 'lucas1', 'london1', 'grace1', 'forever1', 'captain1', 'c2h5oh', 'bubbles1']


def validate_email(value):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
        raise ValidationError(
            'Укажите email правильного вида'
        )

    flag = True
    try:
        User.objects.get(email=value)
    except User.DoesNotExist:
        flag = False
    if flag:
        raise ValidationError(
            'Аккаунт с таким email уже существует'
        )

    if value.split('@')[1] in blocklist:
        raise ValidationError(
            'Укажите email правильного вида'
        )


def validate_password1(value):
    if len(value) < 7:
        raise ValidationError(
            'Длина пароля должна быть больше 6'
        )
    if len(value) > 50:
        raise ValidationError(
            'Длина пароля должна быть меньше 51'
        )
    if value in simplest_passwords or value.isdigit() or value.isalpha():
        raise ValidationError(
            'Слишком простой пароль. Пароль не может состоять только из цифр, или только из букв.'
        )

def validate_password2(value):
    if len(value) > 50:
        raise ValidationError(
            'Длина пароля должна быть меньше 51'
        )


def validate_fio(value):
    value = ' '.join(value)
    if 0 < len(value) < 5:
        raise ValidationError(
            'Введите корректные данные'
        )
    if len(value) > 200:
        raise ValidationError(
            'Длина должна быть меньше 200 символов'
        )
    if len(value.split()) < 2:
        raise ValidationError(
            'ФИО должно состоять из двух и более слов'
        )

