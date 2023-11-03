from utils import *
from pygame import gfxdraw

class CanvasElement():
    def __init__(self, world_coord, render_radius = 30) -> None:
        self.world_coord   = world_coord
        self.render_radius = render_radius
    def render(self, screen, screen_size, coordTrans, sizeTrans):
        sx, sy = coordTrans( self.world_coord )
        sw, sh = screen_size

        sr     = sizeTrans(self.render_radius)
        if sx < -sr or sy < -sr:
            return
        
        if sx > sw + sr or sy > sh + sr:
            return
        


class CanvasLabel(CanvasElement):
    def __init__(self, world_coord, name="package", is_custom_package = False) -> None:
        self.font, _ = gol.getFont(24)
        self.name = name
        text_obj  = self.font.render(name, True, (0,0,0,0))
        text_rect = text_obj.get_rect()
        text_w    = text_rect.width
        text_h    = text_rect.height

        self.passby = False
        self.cond   = 0

        self.label_b   = 2
        self.label_w   = 1.7 * text_w
        self.label_h   = 1.7 * text_h
        self.is_custom_package = is_custom_package
        render_radius = 0.5 * math.sqrt( self.label_w*self.label_w + self.label_h*self.label_h )

        self.has_error = False

        super().__init__(world_coord, render_radius)
    
    def checkMouseOn(self, mouse_pos, coordTrans, sizeTrans):
        sx,sy = coordTrans( self.world_coord )
        slw   = self.label_w
        slh   = self.label_h
        mx,my = mouse_pos
        if ( abs(mx - sx) < 0.5 * slw and abs(my - sy) < 0.5 * slh ):
            self.passby = True
            return True
        
        self.passby = False
        return False
    
    def setCond(self,cond):
        self.cond = cond
    
    def render(self, screen, screen_size, coordTrans, sizeTrans):
        super().render(screen, screen_size, coordTrans, sizeTrans)
        sx,sy = coordTrans(self.world_coord)
        # slw   = sizeTrans( self.label_w )
        # slh   = sizeTrans( self.label_h )
        # slb   = sizeTrans( self.label_b )
        # slb   = max(1, int(slb))
        # font_s = sizeTrans( 24 )
        # new_font,_ = gol.getFont(font_s)

        slw   = self.label_w 
        slh   = self.label_h 
        slb   = self.label_b 
        slb   = max(1, int(slb))
        font_s = 24 
        new_font,_ = gol.getFont(font_s)

        rulx  = sx - 0.5 * slw
        ruly  = sy - 0.5 * slh
        renderCornerRect( screen, gol.BUTTON_LIST_BG_COLOR1, (rulx,ruly), (slw,slh), 0)
        color = gol.TEXT_COLOR
        if (self.has_error == True ):
            color = gol.COLOR_RED
        
        if (self.cond == 1): #被依赖
            color = gol.COLOR_ORANGE
        
        if (self.cond == -1):
            color = gol.COLOR_MID_GREEN

        if (self.passby == True):
            color = gol.COLOR_SKY_BLUE

        renderCornerRect( screen, color, (rulx,ruly), (slw,slh), slb)
        if self.is_custom_package == True:
            renderCornerRect( screen, color, (rulx + 2*slb, ruly + 2*slb), (slw - 4*slb, slh- 4*slb), slb)
        blitTextCenter( screen, self.name, new_font, (sx,sy), color)
    
    def setError(self, state):
        self.has_error = state


class CanvasEdge(CanvasElement):
    def __init__(self, start, end ,b_color = None) -> None:
        render_radius = 0.5 * math.sqrt( (start[0] - end[0])**2 + (start[1] - end[1])**2 )
        world_coord   = (0.5 * start[0] + 0.5 * end[0] , 0.5 * start[1] + 0.5 * end[1]) 
        super().__init__(world_coord, render_radius)

        self.start = start
        self.end   = end
        self.width = 4
        self.cond  = 0
        self.color   = gol.SLIDER_BAR_COLOR
        self.color_b = get_contrast_color(self.color)

        self.b_color = b_color

        self.has_error = False
    
    def setError(self, state):
        self.has_error = state

    def setCond(self,cond):
        self.cond = cond

    def render(self, screen, screen_size, coordTrans, sizeTrans):
        super().render(screen, screen_size, coordTrans, sizeTrans)
        cx = (self.start[0] + self.end[0]) // 2
        cy =  self.start[1] - abs(self.end[0] - self.start[0]) // 2
        # sw       = sizeTrans(self.width)
        # sw       = max(1, math.sqrt(sw))

        n = 20
        for i in range(n):
            x1 = (1 - i/n) * (1 - i/n) * self.start[0] + 2 * (1 - i/n) * i/n * cx + i/n * i/n * self.end[0]
            y1 = (1 - i/n) * (1 - i/n) * self.start[1] + 2 * (1 - i/n) * i/n * cy + i/n * i/n * self.end[1]
            x2 = (1 - (i+1)/n) * (1 - (i+1)/n) * self.start[0] + 2 * (1 - (i+1)/n) * (i+1)/n * cx + (i+1)/n * (i+1)/n * self.end[0]
            y2 = (1 - (i+1)/n) * (1 - (i+1)/n) * self.start[1] + 2 * (1 - (i+1)/n) * (i+1)/n * cy + (i+1)/n * (i+1)/n * self.end[1]

            sx1, sy1 = coordTrans((x1,y1))
            sx2, sy2 = coordTrans((x2,y2))


            color = gol.COLOR_RED
            if (self.has_error == False ):
                color = colorGradient(self.color, self.color_b, i/n)
            
            if (self.cond == 1): #被依赖
                color = gol.COLOR_ORANGE
            
            if (self.cond == -1):
                color = gol.COLOR_MID_GREEN
            
            if (self.b_color != None):
                color = self.b_color

            sw       = self.width + i*6/n
            # gfxdraw.line(screen, int(sx1), int(sy1), int(sx2), int(sy2), self.color)
            renderLine(screen,  color,(int(sx1),int(sy1)), (int(sx2),int(sy2)), int(sw))
