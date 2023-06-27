import random
import sys
import time

import pygame as pg
import math


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し,真理値タプルを返す関数
    引数:こうかとん,または,爆弾SurfaceのRect
    戻り値:横方向,縦方向のはみ出し判定結果（画面内:True/画面外:False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num:こうかとん画像ファイル名の番号
        引数2 xy:こうかとん画像の位置座標タプル
        """
        
        self.img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"./fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        
        self.dire=(5, 0)
        
        self.rt_dct = {
            (0, -5):  pg.transform.flip(pg.transform.rotozoom(self.img, -90, 1.0), True, False),
            (5, -5):  pg.transform.flip(pg.transform.rotozoom(self.img, -45, 1.0), True, False),
            (5, 0):   pg.transform.flip(pg.transform.rotozoom(self.img, 0, 1.0), True, False),
            (5, 5):  pg.transform.flip(pg.transform.rotozoom(self.img, 45, 1.0), True, False),
            (0, 5):   pg.transform.flip(pg.transform.rotozoom(self.img, 90, 1.0), True, False),
            (-5, 5):  pg.transform.rotozoom(self.img, 45, 1.0),
            (-5, 0):  pg.transform.rotozoom(self.img, 0, 1.0),
            (-5, -5): pg.transform.rotozoom(self.img, -45, 1.0)
        }
        
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num:こうかとん画像ファイル名の番号
        引数2 screen:画面Surface
        """
        
        if num == 3:
            self.img = pg.transform.flip(pg.transform.rotozoom(pg.image.load(f"./fig/{num}.png"), 0, 2.0), True, False)
        else:
            self.img = pg.transform.rotozoom(pg.image.load(f"./fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst:押下キーの真理値リスト
        引数2 screen:画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
                
                self.dire = tuple(sum_mv)
                
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
            
        # sum_mvに何らかの値が入っていれば向きを変える
        if sum_mv != [0, 0]:
            self.img = self.rt_dct[(-sum_mv[0], -sum_mv[1])]
            
        screen.blit(self.img, self.rct)

class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color:爆弾円の色タプル
        引数2 rad:爆弾円の半径
        """
        rad_lst = [20, 30, 40, 50]
        color_lst =[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        rad = random.choice(rad_lst)
        color = random.choice(color_lst)
        
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen:画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Beam:
    def __init__(self, bird: Bird) -> None:
        """
        こうかとんがビームを出すようにする
        Args:
            bird: こうかとんのインスタンス
        """
        self.img = pg.image.load(f"./fig/beam.png")
        self.rct = self.img.get_rect()
        
        self.vx, self.vy = bird.dire
        deg = math.degrees(math.atan2(-self.vy, self.vx))
        
        self.img = pg.transform.rotozoom(self.img, deg, 1.0)
        
        self.rct.center = bird.rct.center
        self.rct.centerx += (bird.rct.width/2) * self.vx / 5
        self.rct.centery += (bird.rct.height/2) * self.vy / 5
        
        
    def update(self, screen: pg.Surface):
        """
        爆弾の座標の更新
        Args:
            screen (pg.Surface): 
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    def __init__(self) -> None:
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.x, self.y = 100, HEIGHT-50
        
    def update(self, screen: pg.Surface):
        self.img = self.font.render(f"score:{self.score}", 0, self.color)
        screen.blit(self.img, (self.x, self.y))

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("./fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bomb = [Bomb() for _ in range(NUM_OF_BOMBS)]
    score = Score()
    beam_lst = []

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            # スペースキーが押下されていたらインスタンス生成
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beam_lst.append(Beam(bird))
        
        screen.blit(bg_img, [0, 0])
        
        for b in bomb:
            pass
        
        
        if bomb:
            for i in range(len(bomb)):
                if bird.rct.colliderect(bomb[i].rct):
                    # ゲームオーバー時にこうかとん画像を切り替え,1秒間表示させる
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return

        key_lst = pg.key.get_pressed()
            
        # ビームと爆弾の衝突判定
        for i in range(len(bomb)):
            if beam_lst and bomb:
                for j in range(len(beam_lst)):
                    if not beam_lst[j] or not bomb[i]:
                        continue
                    if beam_lst[j].rct.colliderect(bomb[i].rct):
                        bomb[i] = 0
                        beam_lst[j] = 0

                        bird.change_img(6, screen)
                        score.score += 1
                        pg.display.update()
        
        for b in range(len(beam_lst)):
            if beam_lst[b]:
                if check_bound(beam_lst[b].rct) != (True, True):
                    beam_lst[b] = 0
                        
        if 0 in beam_lst:
            beam_lst.remove(0)
                
        if 0 in bomb:
            bomb.remove(0)
            
        if beam_lst:
            # ビームの位置をアップデート
            for i in range(len(beam_lst)):
                beam_lst[i].update(screen)
            
        for i in range(len(bomb)):
            if bomb[i]:
                bomb[i].update(screen) 
        
        score.update(screen)
        bird.update(key_lst, screen)
        pg.display.update()
        tmr += 1
        
        # デバッグ用　画面外に出た時のリストの削除確認
        # print(len(beam_lst))
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
