# Copyright (c) [2023] [Lantern]
# 
# This file is part of [Livz]
# 
# This project is licensed under the MIT License.
# See LICENSE.txt for details.
import subprocess
import re
from utils import *
from gol import *
from elements import *
import networkx as nx
from bidict import bidict
from input import input_manager
import random

class Component():
    def __init__(self, coord, size, cid) -> None:
        self.canvas = pygame.Surface( size,  pygame.SRCALPHA ) 
        self.coord  = coord
        self.size   = size
        self.cid    = cid

        self.canvas_size  = size
        self.canvas_coord = (0,0)

        self.passby    = False
        self.OnModify  = False
        self.OnResize  = False
        self.OnDrag    = False
        self.ResizeCat = 0
    
    def preRender( self ):
        pass
        # self.canvas.fill(gol.COMPONENT_WINDOW_COLOR1)

    
    def postRender(self, surface):
        vertical_scroll_bar_width    = 5
        horizonal_scroll_bar_height  = 5
        if (self.canvas_size[1] > self.size[1] ):
            # 计算垂直滚动条的高度和位置
            scrollbar_height = self.size[1] * (self.size[1] / self.canvas_size[1])
            scrollbar_y_rel = (self.canvas_coord[1] / self.canvas_size[1]) * self.size[1]

            # 绘制垂直滚动条
            pygame.draw.rect(self.canvas, gol.SCROLL_BAR_COLOR, (self.size[0] - vertical_scroll_bar_width, 0, vertical_scroll_bar_width, self.size[1]))
            pygame.draw.rect(self.canvas, (255, 255, 70), (self.size[0] - vertical_scroll_bar_width, scrollbar_y_rel, vertical_scroll_bar_width, scrollbar_height))

        if (self.canvas_size[0] > self.size[0] ):
            # 计算水平滚动条的宽度和位置
            scrollbar_width = self.size[0] * (self.size[0] / self.canvas_size[0])
            scrollbar_x_rel = (self.canvas_coord[0] / self.canvas_size[0]) * self.size[0]

            # 绘制水平滚动条
            pygame.draw.rect(self.canvas, gol.SCROLL_BAR_COLOR, (0, self.size[1] - horizonal_scroll_bar_height, self.size[0], horizonal_scroll_bar_height))
            pygame.draw.rect(self.canvas, (255, 255, 70), (scrollbar_x_rel, self.size[1] - horizonal_scroll_bar_height, scrollbar_width, horizonal_scroll_bar_height))


        if (self.OnModify == True):
            rect_width = 2
            renderCornerRect(self.canvas, gol.COLOR_BLUE, (0,0), self.size, rect_width)
            if self.passby == True:
                rect_width = 2 
                renderCornerRect(self.canvas, gol.COLOR_ORANGE, (0,0), self.size, rect_width)

            x, y = (0,0)
            w, h = self.size
            circle_radius = 8  
            circle_color  = gol.COLOR_ORANGE 
            if self.ResizeCat == 1:
                renderCircle(self.canvas, circle_color, (x, y), 1.6*circle_radius, 2)
            elif self.ResizeCat == 2:
                renderCircle(self.canvas, circle_color, (x + w // 2, y), circle_radius, 2)
            elif self.ResizeCat == 3:
                renderCircle(self.canvas, circle_color, (x + w, y), 1.6*circle_radius, 2)
            elif self.ResizeCat == 4:
                renderCircle(self.canvas, circle_color, (x + w, y + h // 2), circle_radius, 2)
            elif self.ResizeCat == 5:
                renderCircle(self.canvas, circle_color, (x + w, y + h), 1.6*circle_radius, 2)
            elif self.ResizeCat == 6:
                renderCircle(self.canvas, circle_color, (x + w // 2, y + h), circle_radius, 2)
            elif self.ResizeCat == 7:
                renderCircle(self.canvas, circle_color, (x, y + h), 1.6*circle_radius, 2)
            elif self.ResizeCat == 8:
                renderCircle(self.canvas, circle_color, (x, y + h // 2), circle_radius, 2)
        surface.blit(self.canvas, self.coord)
    
    def render(self, surface):
        self.preRender()
        self.postRender(surface)
    
    def onResize(self, new_size):
        nsx , nsy = new_size
        nsx = max(10, nsx)
        nsy = max(10, nsy)
        self.size = (nsx, nsy)

    def onMouseMotion(self, mouse_x, mouse_y):
        x, y = self.coord
        w, h = self.size
        if self.OnDrag == True:
            dx = input_manager.mouse_x_vel
            dy = input_manager.mouse_y_vel
            self.coord = ( x+dx, y+dy )
        
        if self.OnResize == True:
            dx = input_manager.mouse_x_vel
            dy = input_manager.mouse_y_vel
            if self.ResizeCat == 1:
                self.coord = (  x+dx, y+dy )
                self.onResize( ( w - dx, h - dy) )
            if self.ResizeCat == 2:
                self.coord = (  x, y+dy )
                self.onResize( ( w , h - dy) )
            if self.ResizeCat == 3:
                self.coord = (  x, y+dy )
                self.onResize( ( w + dx, h - dy) )
            if self.ResizeCat == 4:
                self.coord = (  x, y )
                self.onResize( ( w + dx, h) )
            if self.ResizeCat == 5:
                self.coord = (  x, y )
                self.onResize( ( w + dx, h + dy) )
            if self.ResizeCat == 6:
                self.coord = (  x, y )
                self.onResize( ( w, h + dy) )
            if self.ResizeCat == 7:
                self.coord = (  x+dx, y )
                self.onResize( ( w - dx, h + dy) )
            if self.ResizeCat == 8:
                self.coord = (  x+dx, y )
                self.onResize( ( w - dx, h ) )
            
            self.canvas = pygame.Surface( self.size,  pygame.SRCALPHA ) 

        x, y = self.coord
        w, h = self.size

        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
            self.passby = True
        else:
            self.passby = False
        
        threshold_distance = 20  # 设置一个阈值距离

        corners_and_edges = [
            (x, y),                   # 左上角
            (x + w // 2, y),          # 上边中点
            (x + w, y),               # 右上角
            (x + w, y + h // 2),      # 右边中点
            (x + w, y + h),           # 右下角
            (x + w // 2, y + h),      # 下边中点
            (x, y + h),               # 左下角
            (x, y + h // 2)           # 左边中点
        ]

        self.ResizeCat = 0 
        # 根据鼠标位置相对于各角落的距离来设置ResizeCat的值
        for i, (corner_x, corner_y) in enumerate(corners_and_edges):
            if distance(mouse_x, mouse_y, corner_x, corner_y) < threshold_distance:
                self.ResizeCat = i + 1 
                return
        
        # 移动canvas
        # if self.passby:
        #     cw,ch = self.canvas_size
        #     cx,cy = self.canvas_coord

        #     speed_w = 0.0
        #     speed_h = 0.0
        #     if ch > h:
        #         if mouse_y > 0.7 * h:
        #             speed_h = mouse_y - 0.7*h
        #         if mouse_y < 0.3 * h:
        #             speed_h = - 0.3*h + mouse_y
        #     if cw > w:
        #         if mouse_x > 0.7 * w:
        #             speed_w = mouse_x - 0.7*w
        #         if mouse_x < 0.3 * w:
        #             speed_w = - 0.3*w + mouse_x
            
        #     kx = abs(cw - w) * 0.001
        #     ky = abs(ch - h) * 0.001
        #     new_cx  = min( cx + speed_w * kx , cw - w)
        #     new_cy  = min( cy + speed_h * ky , ch - h)

        #     new_cx  = max( new_cx, 0 )
        #     new_cy  = max( new_cy, 0 )
        #     self.canvas_coord = (new_cx, new_cy)



    def onMouseClick(self, mouse_x, mouse_y, btn):
        if self.OnModify:
            if self.passby:
                if btn == gol.MOUSEBUTTON_LEFT:
                    if self.ResizeCat == 0:
                        self.OnDrag = True
                    else:
                        self.OnResize = True
        else:
            if self.passby:
                if btn == gol.MOUSEBUTTON_WHEELDOWN:
                    w, h    = self.size
                    cw,ch   = self.canvas_size
                    cx,cy   = self.canvas_coord
                    ky      = 20
                    new_cy  = min( cy + 2 * ky , ch - h)
                    new_cy  = max( new_cy, 0 )
                    self.canvas_coord = (cx, new_cy)
                if btn == gol.MOUSEBUTTON_WHEELUP:
                    w, h    = self.size
                    cw,ch   = self.canvas_size
                    cx,cy   = self.canvas_coord
                    ky      = -20
                    new_cy  = min( cy + 2 * ky , ch - h)
                    new_cy  = max( new_cy, 0 )
                    self.canvas_coord = (cx, new_cy)

    
    def onMouseUp(self, mouse_x, mouse_y, btn):
        if self.OnModify:
            if btn == gol.MOUSEBUTTON_LEFT:
                self.OnDrag   = False
                self.OnResize = False
    
    def onKeyInput(self, key, unicode):
        pass

    def update(self):
        # 在这里进行任何需要的更新
        if self.OnDrag:
            # 更新坐标等
            pass

class StateBar(Component):
    class Task:
        def __init__(self, name, progress) -> None:
            self.name     = name
            self.progress = progress


    def __init__(self, coord, size , cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.recent_title = "Ready"
        self.bg_color     = gol.STATE_WINDOW_COLOR
        self.color        = self.bg_color
        self.title_color  = gol.COLOR_WHITE

        self.flash_opacity = 0.0

        self.tasks        = []
    
    def flash(self, new_title, type = "normal"):
        self.recent_title  = new_title
        self.flash_opacity = 0.5

        if (type == "warning"):
            self.bg_color = gol.COLOR_DARK_ORANGE
        elif (type == "error"):
            self.bg_color = gol.COLOR_DARK_RED
        elif (type == "good"):
            self.bg_color = gol.COLOR_DARK_GREEN
        else:
            self.bg_color = gol.STATE_WINDOW_COLOR
        self.title_color  = colorGradient( self.bg_color, gol.COLOR_WHITE, 0.8)


    
    def preRender( self ):
        # super().preRender()
        color = self.bg_color
        if(self.flash_opacity > 0.04):
            self.flash_opacity -= 0.007
            color = colorGradient( self.bg_color, gol.COLOR_WHITE, self.flash_opacity )
        else:
            self.flash_opacity = 0.0
        self.canvas.fill( color )
        w,h   = self.size
        mx,my = 0.5*w , 0.5*h

        font_size = h * 0.9
        font, real_size = gol.getFont(font_size)
        blitTextCenter( self.canvas, self.recent_title, font, (mx,my), self.title_color)
    
    def postRender(self, surface):
        surface.blit(self.canvas, self.coord)

class Label(Component):
    def __init__(self, coord, size, content = "label", color = gol.COLOR_YELLOW, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.content = content
        self.color = color

    def preRender( self ):
        self.canvas.fill(gol.COLOR_TRANS)
        w,h   = self.size
        mx,my = 0.5*w , 0.5*h

        font_size = min( h * 0.9, (2.1*self.size[0]/len(self.content) ))
        font, real_size = gol.getFont(font_size)
        blitTextCenter( self.canvas, self.content, font, (mx,my), self.color)
    
    def onResize(self, new_size):
        super().onResize(new_size)
        self.canvas_size = new_size



class Switch(Component):
    def __init__(self, coord, size, callback, title = "switch", on_color = gol.TEXT_COLOR, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.title      = title
        self.on_color   = on_color
        self.pass_color = colorGradient(on_color, gol.BUTTON_BG_COLOR2, 0.6)
        self.color      = gol.TEXT_COLOR

        self.static_back_surf = create_gradient_surface_with_radius(size[0], size[1], gol.BUTTON_BG_COLOR2, gol.BUTTON_BG_COLOR1 , radius=0.0 , dir="horizontal")
        self.card_out_shadow  = create_soft_shadow(size[0], size[1], radius=0.0, blur=60)
        self.need_regene_shadow = False
        self.callback   = callback

        self.on       = False
    
    def preRender( self ):
        super().preRender()
        self.canvas.blit(self.static_back_surf, (0,0))
        w,h   = self.size
        mx,my = 0.5*w , 0.5*h


        if self.passby == True:
            renderCornerRect( self.canvas, self.pass_color, (0,0), self.size, 0)

        if self.on == True:
            renderCornerRect( self.canvas, self.color, (0,0), self.size , 4)
        else:
            renderCornerRect( self.canvas, self.color, (0,-3), (w,h+6) , 2)
        

        font_size = h * 0.9
        font, real_size = gol.getFont(font_size)
        blitTextCenter( self.canvas, self.title, font, (mx,my), self.color)
        
    def postRender(self, surface):
        x,y  = self.coord
        if(self.OnModify == False and self.need_regene_shadow == False):
            surface.blit(self.card_out_shadow , (x-10, y + 10) )
        
        if(self.OnModify == False and self.need_regene_shadow == True):
            self.card_out_shadow  = create_soft_shadow(self.size[0], self.size[1], radius=0.0, blur=60)
            self.need_regene_shadow = False

        super().postRender(surface)

    def onResize(self, new_size):
        super().onResize( new_size )
        self.canvas_size = self.size
        self.need_regene_shadow = True
    
    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 
        
        if self.passby == True:
            if btn == gol.MOUSEBUTTON_LEFT:
                self.on = not self.on
                self.callback( self.on )


class Button(Component):
    def __init__(self, coord, size, callback, title="button", on_color=gol.BUTTON_HOVER_COLOR, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.title      = title
        self.on_color   = on_color
        self.pass_color = colorGradient(on_color, gol.BUTTON_BG_COLOR2, 0.8)
        self.color  = gol.TEXT_COLOR
        self.radius = 0.7

        self.mask    = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
        self.static_back_surf = create_gradient_surface_with_radius(size[0], size[1], gol.BUTTON_BG_COLOR2, gol.BUTTON_BG_COLOR1 , radius=self.radius , dir="horizontal")
        self.card_out_shadow  = create_soft_shadow(size[0], size[1], radius=self.radius, blur=60)
        self.need_regene_shadow = False
        self.callback = callback


    def preRender(self):
        super().preRender()
        w, h = self.size
        mx, my = 0.5 * w, 0.5 * h

        self.canvas.blit(self.static_back_surf, (0,0))
        # renderCornerRect(self.canvas, gol.BUTTON_SIDE_COLOR, (0, 0), (w,h), 2)

        if self.passby:
            renderCornerRect(self.canvas, self.pass_color, (0, 0), self.size, 0)

        font_size = min( h * 0.9, (2.1*self.size[0]/len(self.title) ))
        font, real_size = gol.getFont(font_size)
        blitTextCenter(self.canvas, self.title, font, (mx, my), self.color)
        w,h = self.size
        pygame.draw.rect(self.mask, (255, 255, 255), self.mask.get_rect(), 0, border_radius=int(min(w, h)*self.radius/2))
        self.canvas.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
    def onResize(self, new_size):
        super().onResize(new_size)
        self.canvas_size = self.size

        self.mask    = pygame.Surface((new_size[0], new_size[1]), pygame.SRCALPHA)
        self.static_back_surf = create_gradient_surface_with_radius(new_size[0], new_size[1], gol.BUTTON_BG_COLOR2, gol.BUTTON_BG_COLOR1 , radius=self.radius , dir="horizontal")
        self.need_regene_shadow = True
    
    def postRender(self, surface):
        x,y  = self.coord
        if(self.OnModify == False and self.need_regene_shadow == False):
            surface.blit(self.card_out_shadow , (x-10, y + 10) )
        
        if(self.OnModify == False and self.need_regene_shadow == True):
            self.card_out_shadow  = create_soft_shadow(self.size[0], self.size[1], radius=self.radius, blur=60)
            self.need_regene_shadow = False

        super().postRender(surface)
    

    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 
        
        if self.passby:
            if btn == gol.MOUSEBUTTON_LEFT:
                gol.state_bar.flash( self.title )
                self.callback()

class ListButton(Component):
    def __init__(self, coord, size, callback, title="button", pass_color=gol.COLOR_LIGHT_YELLOW_TRANS, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.title      = title
        self.pass_color = pass_color
        self.color      = gol.TEXT_COLOR
        self.callback   = callback
        self.animate_t  = 0
        self.static_background_surf = create_gradient_surface_with_radius(size[0], size[1], gol.LIST_BUTTON_BG_COLOR1, gol.LIST_BUTTON_BG_COLOR2, 0)

    def preRender(self):
        super().preRender()
        self.canvas.fill(gol.LIST_BUTTON_BG_COLOR)
        # self.canvas.blit(self.static_background_surf, (0,0))

        w, h = self.size
        mx, my = 0.5 * w, 0.5 * h

        
        if self.passby:
            self.animate_t = min( self.animate_t + 0.05 , 1.0)
            k = self.animate_t ** 2
            p_color = colorGradient(gol.COLOR_TRANS, self.pass_color, k)
            renderCornerRect(self.canvas, p_color, (0, 0), self.size, 0)
        
        else:
            self.animate_t = max( self.animate_t - 0.05 , 0.0)
            # k = self.animate_t ** 2
            # p_color = colorGradient(gol.COLOR_TRANS, self.pass_color, k)
            # renderCornerRect(self.canvas, p_color, (0, 0), self.size, 0)
        

        font_size = min( h * 0.8, (2.4*self.size[0]/len(self.title) ))
        font, real_size = gol.getFont(font_size)
        blitTextLeft(self.canvas, self.title, font, (10, my), self.color)

    def onResize(self, new_size):
        super().onResize(new_size)
        self.canvas_size = self.size
        self.static_background_surf = create_gradient_surface_with_radius(new_size[0], new_size[1], gol.LIST_BUTTON_BG_COLOR1, gol.LIST_BUTTON_BG_COLOR2, 0)

    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 
        
        if self.passby:
            if btn == gol.MOUSEBUTTON_LEFT:
                gol.state_bar.flash( self.title)
                self.callback()

class ButtonList(Component):
    def __init__(self, coord, size, btn_h = 30,  button_list = [], cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.mid_canvas     = pygame.Surface( size,  pygame.SRCALPHA ) 
        self.button_list    = button_list
        self.button_height  = btn_h
        self.radius         = 0.2
        self.need_regene_shadow = False
        self.static_back_surf = create_gradient_surface_with_radius(size[0], size[1], gol.BUTTON_LIST_BG_COLOR1, gol.BUTTON_LIST_BG_COLOR2 , radius=self.radius)
        self.card_out_shadow  = create_soft_shadow(size[0], size[1], radius=self.radius, blur=60)

        # 创建圆角
        self.mask    = pygame.Surface((size[0], size[1]), pygame.SRCALPHA)
        self.current_button_count = 0
    
    def appendButton(self, call_back, title="list_button", cid = -1):
        button = ListButton( (0, self.current_button_count * self.button_height), (self.size[0] , self.button_height), call_back, title , cid=cid)
        self.button_list.append(button)
        self.current_button_count += 1
        self.canvas_size    = (self.size[0], self.current_button_count * self.button_height)
        self.mid_canvas     = pygame.Surface( self.canvas_size,  pygame.SRCALPHA ) 

    def preRender(self):
        super().preRender()
        self.canvas.fill(gol.COLOR_TRANS)
        self.canvas.blit(self.static_back_surf, (0,0))
        w, h = self.size

        for button in self.button_list:
            button.preRender()
    
    def postRender(self, surface):

        for button in self.button_list:
            button.postRender(self.mid_canvas)

        cx,cy = self.canvas_coord
        self.canvas.blit(self.mid_canvas, (-cx,-cy))

        x,y  = self.coord
        w, h = self.size
        if(self.OnModify == False and self.need_regene_shadow == False):
            surface.blit(self.card_out_shadow , (x-15, y + 15) )
        
        if(self.OnModify == False and self.need_regene_shadow == True):
            self.card_out_shadow  = create_soft_shadow(self.size[0], self.size[1], radius=self.radius, blur=60)
            self.need_regene_shadow = False
        
        pygame.draw.rect(self.mask, (255, 255, 255), self.mask.get_rect(), 0, border_radius=int(min(w, h)*self.radius/2))
        self.canvas.blit(self.mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        super().postRender(surface)

        # blitTextCenter(self.canvas, self.title, gol.font1, (mx, my), self.color)

    def onResize(self, new_size):
        super().onResize(new_size)
        x,y = self.size
        self.canvas_size = (x, self.canvas_size[1])
        self.mid_canvas  = pygame.Surface( self.canvas_size,  pygame.SRCALPHA ) 
        for button in self.button_list:
            button.size        = (x, button.size[1])
            button.canvas_size = (x, button.canvas_size[1])
        
        self.static_back_surf   = create_gradient_surface_with_radius(new_size[0], new_size[1], gol.BUTTON_LIST_BG_COLOR1, gol.BUTTON_LIST_BG_COLOR2 , radius=self.radius)
        self.mask               = pygame.Surface((new_size[0], new_size[1]), pygame.SRCALPHA)
        self.need_regene_shadow = True

    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 
        
        cx,cy = self.canvas_coord
        if self.passby:
            for button in self.button_list:
                button.onMouseClick(mouse_x + cx, mouse_y + cy, btn)
    
    def onMouseMotion(self, mouse_x, mouse_y):
        super().onMouseMotion(mouse_x, mouse_y)
        if self.OnModify == True:
            return 
        
        cx,cy = self.canvas_coord
        for button in self.button_list:
            rel_x , rel_y = mouse_x - self.coord[0] + cx , mouse_y - self.coord[1] + cy
            button.onMouseMotion(rel_x , rel_y )
        
        
class Slider(Component):
    def __init__(self, coord, size, min_value, max_value, callback, title="slider", slider_color=gol.SLIDER_BAR_COLOR, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.title = title
        self.slider_color = slider_color
        self.pass_color   = colorGradient(slider_color, gol.COLOR_WHITE, 0.6)
        self.color = gol.TEXT_COLOR
        self.slider_width = min(size[0] * 0.04, 20)

        self.min_value = min_value
        self.max_value = max_value
        self.callback = callback

        self.current_value = min_value

        self.dragging = False

    def preRender(self):
        super().preRender()
        self.canvas.fill(gol.SLIDER_BG_COLOR)
        w, h = self.size
        mx, my = 0.5 * w, 0.5 * h

        puil_h     = 0.08 * h
        # puil_color = colorGradient(self.slider_color, gol.COLOR_BLACK, 0.4)
        puil_color = gol.SLIDER_TRACK_COLOR

        renderCornerRect(self.canvas, puil_color, (0, my - 0.5*puil_h), (w, puil_h), 0)

        slider_position = ((self.current_value - self.min_value) / (self.max_value - self.min_value)) * (w-self.slider_width)

        renderCornerRect(self.canvas, gol.SLIDER_BAR_COLOR, (0, my - 0.5*puil_h), (slider_position, puil_h), 0)
        pygame.draw.rect(self.canvas, gol.SLIDER_BAR_COLOR, (slider_position, 0, self.slider_width, h))



        font_size = h * 0.6
        font,real_size = gol.getFont(font_size)

        shown_str = float_to_str(self.min_value) + "  <  " + self.title + "  >  " +  float_to_str(self.max_value)
        blitTextCenter(self.canvas, shown_str, font, (mx, h - 0.4*real_size), self.color)
        # blitTextLeft(self.canvas, float_to_str(self.min_value), font, (0, h - 0.4*real_size), self.color)
        # blitTextRight(self.canvas, float_to_str(self.max_value), font, (w, h - 0.4*real_size), self.color)

        if self.passby:
            pygame.draw.rect(self.canvas, self.pass_color, (slider_position, 0, self.slider_width, h))
            mid_value = 0.5 * ( self.min_value +  self.max_value )
            if self.current_value < mid_value:
                blitTextLeft(self.canvas, float_to_str(self.current_value), font, (slider_position +  self.slider_width , 0.4*real_size), gol.SLIDER_BAR_COLOR)
            else:
                blitTextRight(self.canvas, float_to_str(self.current_value), font, (slider_position , 0.4*real_size), gol.SLIDER_BAR_COLOR)



    def onResize(self, new_size):
        super().onResize(new_size)
        self.canvas_size  = self.size
        self.slider_width = min(self.size[0] * 0.04, 20)

    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 
        
        if self.passby:
            if btn == gol.MOUSEBUTTON_LEFT:
                self.dragging = True

    def onMouseUp(self, mouse_x, mouse_y, btn):
        super().onMouseUp(mouse_x, mouse_y, btn)
        if btn == gol.MOUSEBUTTON_LEFT:
            self.dragging = False

    def onMouseMotion(self, mouse_x, mouse_y):
        super().onMouseMotion(mouse_x, mouse_y)
        if self.dragging:
            x, y = self.coord
            w, h = self.size

            dx = mouse_x - x
            self.current_value = self.min_value + ((self.max_value - self.min_value) * (dx / w))
            self.current_value = max(self.min_value, min(self.max_value, self.current_value))
            self.callback(self.current_value)


class Graph(Component):
    class Curve():
        def __init__(self, name = "curve", color = gol.COLOR_GREEN) -> None:
            self.name  = name
            self.color = color
            self.data  = []
            self.current_x = 0
            self.min_X = 0
            self.max_X = 20
            self.min_Y = 0
            self.max_Y = 10
            self.data_count = 0

        def feedData(self, dat):
            x = self.current_x + 1
            self.current_x = x
            self.data_count += 1
            if x < self.min_X:
                self.min_X = x
            if x > self.max_X:
                self.max_X = x
            if dat < self.min_Y:
                self.min_Y = dat
            if dat > self.max_Y:
                self.max_Y = dat
            self.data.append(dat)

        def reset(self):
            self.data  = []
            self.current_x = 0
            self.min_X = 0
            self.max_X = 20
            self.min_Y = 0
            self.max_Y = 10
            self.data_count = 0
            

    def __init__(self, coord, size, title="graph", cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.title      = title
        self.curves     = {}
        self.maxY       = 10
        self.minY       = 0
        self.YGap       = self.maxY - self.minY
        self.maxX       = 20
        self.res_x      = 1
        self.data_count = 0
    
    def updateMaxD(self):
        for curve in self.curves.values():
            if curve.max_Y > self.maxY:
                self.maxY = curve.max_Y
            if curve.min_Y < self.minY:
                self.minY = curve.min_Y
            if curve.max_X > self.maxX:
                self.maxX = curve.max_X
            if curve.data_count > self.data_count:
                self.data_count = curve.data_count
        self.YGap       = self.maxY - self.minY
        max_item   = self.size[0]
        self.res_x = max(1, math.floor(self.data_count / max_item))
    
    def reset(self):
        self.maxY       = 10
        self.minY       = 0
        self.YGap       = self.maxY - self.minY
        self.maxX       = 20
        self.res_x      = 1
        self.data_count = 0
        for curve in self.curves.values():
            curve.reset()
    
    def createCurve(self,name, color):
        self.curves[name] = self.Curve(name, color)
    
    def appendData(self, name, data):
        if name in self.curves:
            self.curves[name].feedData(data)
        else:
            self.curves[name] = self.Curve(name, gol.COLOR_DARK_RED)

    def getCoord(self, x,y):
        w,h = self.size
        coord_y = h - h*(y - self.minY) / (self.YGap)
        coord_x = w*x / self.maxX
        return (coord_x, coord_y)

    def hasCurve(self,name):
        if name in self.canvas:
            return True
        else:
            return False


    def preRender(self):
        super().preRender()
        w, h   = self.size
        mx, my = 0.5 * w, 0.5 * h
        
        self.canvas.fill(gol.COLOR_BLACK)
        renderCornerRect(self.canvas, gol.COLOR_DARK_WHITE, (0, 0), (w,h), 2)
        renderLine(self.canvas, gol.COLOR_WHITE, (0,0),(0,h),2)
        renderLine(self.canvas, gol.COLOR_WHITE, (0,h-1),(w,h-1),2)

        font_size = min( 26, h*0.1 )
        font, real_size = gol.getFont(font_size)
        blitTextCenter(self.canvas, self.title, font, (mx, font_size*0.6), gol.COLOR_WHITE)
        self.updateMaxD()

        for curve in self.curves.values():
            x = 0 
            while x < curve.current_x - self.res_x:
                p1 = self.getCoord(x, curve.data[x])
                p2 = self.getCoord(x+self.res_x, curve.data[x+self.res_x])
                renderLine(self.canvas, curve.color, p1,p2,1)
                x += self.res_x


        max_y_str = str( self.maxY )
        max_x_str = str( self.maxX )
        blitTextLeft(self.canvas, max_y_str, font, (5, font_size*0.6), gol.COLOR_WHITE)

        max_x_str_len = 0.5*font_size * len(max_x_str)
        blitTextLeft(self.canvas, max_x_str, font, (w - max_x_str_len - 5, h - font_size*0.6), gol.COLOR_WHITE)
    
    def postRender(self, surface):
        super().postRender(surface)
        
    def onResize(self, new_size):
        super().onResize(new_size)
        self.canvas_size  = self.size
    

    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 





class MiniTerminal(Component):
    def __init__(self, coord, size, buffer_rows, font_size = 14, title="mini terminal", text_color=gol.COLOR_WHITE, bg_color = gol.COLOR_BLACK, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.title               = title
        self.text_color          = text_color
        self.bg_color            = bg_color

        self.font_size           = font_size
        self.font                = gol.getMonoFont(font_size)[0]
        self.title_font_size     = min(26, max(14, self.size[1] * 0.2 ))
        self.title_font          = gol.getFont(self.title_font_size)[0]
        self.buffer_rows         = buffer_rows
        self.buffer              = ""
        self.row_dis             = 1.00
        self.line_height         = self.row_dis * self.font_size
        self.lines               = [""]
        self.command             = ""
        self.current_command     = ""
        self.history_commands    = []
        self.command_library     = ["clear", "setTextColor ", "setBgColor ", "exportToFile ","ip"]
        self.command_pos         = 0
        self.last_line_width     = 0

        self.cursor_time     = 0
        self.cursor_pos      = 0
        self.modified_h      = size[1] - 1.3*self.line_height
        self.canvas_size  =  (size[0], self.modified_h) 
        self.mid_canvas   = pygame.Surface(self.canvas_size,  pygame.SRCALPHA ) 
        self.fixing       = False
    
    def reGenerateLines(self):
        self.lines = []
        line_width = 0
        line = ""
        for i, char in enumerate(self.buffer):
            if char == '\n':  # 检测到换行符，直接分行
                self.lines.append(line)
                line_width = 0
                line = ""
                continue

            char_width, _ = self.font.size(char)
            line_width   += char_width
            if line_width > self.size[0] - self.font_size:
                self.lines.append(line)
                line_width = char_width
                line = ""
            line += char

        if( line != "" ):
            self.lines.append(line)
            self.last_line_width = line_width

        min_mid_canvas_height = self.modified_h
        mid_canvas_height     = max( len(self.lines) * self.line_height ,  min_mid_canvas_height)
        self.canvas_size      = (self.size[0], mid_canvas_height)
        self.mid_canvas       = pygame.Surface( (self.size[0], mid_canvas_height),  pygame.SRCALPHA ) 
    
    def feedChar(self,char):
        self.buffer  += char
        char_width, _ = self.font.size(char)

        cx,cy = self.canvas_coord
        cw,ch = self.canvas_size
        modified_y = self.modified_h
        canvas_coord_y_change = 0

        if char == '\n':  # 检测到换行符，直接分行
            new_line = ""
            self.lines.append(new_line)
            self.last_line_width = 0

            if (ch >  modified_y and (ch - cy - modified_y) < 10):
                canvas_coord_y_change = self.line_height
            if( len(self.lines) > self.buffer_rows ):
                line0_len = len(self.lines[0])
                self.lines.pop(0)
                self.buffer = self.buffer[line0_len:]
                canvas_coord_y_change = 0

            min_mid_canvas_height = self.modified_h
            mid_canvas_height = max( len(self.lines) * self.line_height ,  min_mid_canvas_height)
            self.canvas_size  = (self.size[0], mid_canvas_height)
            self.mid_canvas   = pygame.Surface( self.canvas_size,  pygame.SRCALPHA ) 

            self.canvas_coord = (0, self.canvas_coord[1] + canvas_coord_y_change)
            return

        self.last_line_width += char_width
        if self.last_line_width > self.size[0] - self.font_size:
            new_line = "".join(char)
            self.lines.append(new_line)
            self.last_line_width = char_width

            if (ch >  modified_y and (ch - cy - modified_y) < 10):
                canvas_coord_y_change = self.line_height
            if( len(self.lines) > self.buffer_rows ):
                line0_len = len(self.lines[0])
                self.lines.pop(0)
                self.buffer = self.buffer[line0_len:]
                canvas_coord_y_change = 0

            min_mid_canvas_height = self.modified_h
            mid_canvas_height = max( len(self.lines) * self.line_height ,  min_mid_canvas_height)
            self.canvas_size  = (self.size[0], mid_canvas_height)
            self.mid_canvas   = pygame.Surface( self.canvas_size,  pygame.SRCALPHA ) 
            self.canvas_coord = (0, self.canvas_coord[1] + canvas_coord_y_change)
        else:
            self.lines[-1] += char
              
    
    def feedString(self, string):
        for char in string:
            self.feedChar(char)
    
    def getCursorX(self, pos):
        whole_str = "> "+self.command
        cursor_x  = 0
        for char in whole_str[:pos+2]:
            w,_ = self.font.size(char)
            cursor_x += w
        return cursor_x+0.15*self.font_size
     
    def preRender(self):
        super().preRender()
        self.canvas.fill(self.bg_color)
        self.mid_canvas.fill(self.bg_color)
        # self.mid_canvas.fill(gol.COLOR_BLUE)
        begin_line = math.floor(self.canvas_coord[1] / self.line_height)
        end_line   = math.floor((self.canvas_coord[1] + self.modified_h)/ self.line_height)
        for i, line in enumerate(self.lines[begin_line:end_line], start=begin_line):
            blitTextLeft( self.mid_canvas, line, self.font, (2, (i+0.5)*self.line_height) , self.text_color)
    
    # 重写基类postRender函数，主要是进度条部分有冲突
    def postRender(self, surface):
        w,h   = self.size
        x,y   = self.coord
        cx,cy = self.canvas_coord
        self.canvas.blit(self.mid_canvas, (-cx,-cy))

        command_color = get_contrast_color( self.bg_color )
        cursor_color = command_color
        command_str = "> " + self.command
        blitTextLeft(self.canvas, command_str, self.font, (2, 0.5 * (h+self.modified_h)), command_color)
        renderLine(self.canvas, cursor_color, (0, self.modified_h), (w, self.modified_h), 1)
        if self.fixing:
            cursor_x = self.getCursorX(self.cursor_pos)
            cursor_T = 200
            if self.cursor_time < cursor_T:
                renderLine(self.canvas, cursor_color, (cursor_x, self.modified_h + 4), (cursor_x, h - 4), 2)
            if self.cursor_time > 2*cursor_T:
                self.cursor_time = 0
            self.cursor_time += 1

        blitTextLeft( surface, self.title, self.title_font, (x, y - 0.5*self.title_font_size), gol.TEXT_COLOR)

        # 重写后的super().postRender
        vertical_scroll_bar_width    = 5
        modified_size_y = self.modified_h
        if (self.canvas_size[1] > modified_size_y):
            # 计算垂直滚动条的高度和位置
            scrollbar_height = max(3, modified_size_y * (modified_size_y / self.canvas_size[1]))
            scrollbar_y_rel  = (self.canvas_coord[1] / self.canvas_size[1]) * modified_size_y

            # 绘制垂直滚动条
            pygame.draw.rect(self.canvas, gol.SCROLL_BAR_COLOR, (self.size[0] - vertical_scroll_bar_width, 0, vertical_scroll_bar_width, modified_size_y))
            pygame.draw.rect(self.canvas, (255, 255, 70), (self.size[0] - vertical_scroll_bar_width, scrollbar_y_rel, vertical_scroll_bar_width, scrollbar_height))

        if (self.OnModify == True):
            rect_width = 2
            renderCornerRect(self.canvas, gol.COLOR_BLUE, (0,0), self.size, rect_width)
            if self.passby == True:
                rect_width = 2 
                renderCornerRect(self.canvas, gol.COLOR_ORANGE, (0,0), self.size, rect_width)

            x, y = (0,0)
            w, h = self.size
            circle_radius = 8  
            circle_color  = gol.COLOR_ORANGE 
            if self.ResizeCat == 1:
                renderCircle(self.canvas, circle_color, (x, y), 1.6*circle_radius, 2)
            elif self.ResizeCat == 2:
                renderCircle(self.canvas, circle_color, (x + w // 2, y), circle_radius, 2)
            elif self.ResizeCat == 3:
                renderCircle(self.canvas, circle_color, (x + w, y), 1.6*circle_radius, 2)
            elif self.ResizeCat == 4:
                renderCircle(self.canvas, circle_color, (x + w, y + h // 2), circle_radius, 2)
            elif self.ResizeCat == 5:
                renderCircle(self.canvas, circle_color, (x + w, y + h), 1.6*circle_radius, 2)
            elif self.ResizeCat == 6:
                renderCircle(self.canvas, circle_color, (x + w // 2, y + h), circle_radius, 2)
            elif self.ResizeCat == 7:
                renderCircle(self.canvas, circle_color, (x, y + h), 1.6*circle_radius, 2)
            elif self.ResizeCat == 8:
                renderCircle(self.canvas, circle_color, (x, y + h // 2), circle_radius, 2)
        surface.blit(self.canvas, self.coord)

    
    def setTextColorCmd(self, params):
        # 设置文字颜色
        if len(params) != 3:
            self.feedString("\n> need 3 params: [r] [g] [b]!\n")
            return
        
        try:
            r = int(params[0])
            g = int(params[1])
            b = int(params[2])
        except ValueError:
            self.feedString("\n> invalid params: [r] [g] [b] must be integer!\n")
            return
        
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))
        
        self.text_color = (r,g,b,255)
    
    def setBgColorCmd(self, params):
        # 设置文字颜色
        if len(params) != 3:
            self.feedString("\n> need 3 params: [r] [g] [b]!\n")
            return
        
        try:
            r = int(params[0])
            g = int(params[1])
            b = int(params[2])
        except ValueError:
            self.feedString("\n> invalid params: [r] [g] [b] must be integer!\n")
            return
        
        r = max(0, min(r, 255))
        g = max(0, min(g, 255))
        b = max(0, min(b, 255))
        
        self.bg_color = (r,g,b,255)
    
    def exportToFileCmd(self, params):
        # 将终端内容导出到文件
        if len(params) != 1:
            self.feedString("\n> need 1 params: [file path]!\n")
            return
    
        file_path  = params[0]
        whole_path = gol.CALLBACK_PATH[:gol.CALLBACK_PATH.rfind('/')] + "/" + file_path
        with open(whole_path, 'w') as file:
            file.write(self.buffer)
        
        self.feedString("> write to file " + whole_path + " successfully!")
    
    def ipShowCmd(self, params):
        try:
            result = subprocess.check_output(['ip','a'], universal_newlines=True)
            ipv4_addresses = re.findall(r'inet (\d+\.\d+\.\d+\.\d+)', result)
            ipv4_addr_str  = "\n> ipv4 addresses found:\n"
            for addr in ipv4_addresses:
                ipv4_addr_str += addr + "\n"
            self.feedString(ipv4_addr_str)
        except subprocess.CalledProcessError as e:
            self.feedString("\n> error occurred!\n")

    
    # 暂时不要执行这个功能，有些指令会阻塞
    # async def uniCommand(self):
    #     process = await asyncio.create_subprocess_shell(
    #         self.command,
    #         stdout = asyncio.subprocess.PIPE,
    #         stderr = asyncio.subprocess.PIPE
    #     )
    #     stdout, stderr = await process.communicate()
    #     self.feedString(stdout.decode())
    #     if stderr:
    #         self.feedString("<stderr>:" + stderr.decode())

        
    def autoCompleter(self):
        # 匹配最近的公共字符串
        current_text = self.command
        matching_commands = [cmd for cmd in self.command_library if cmd.startswith(current_text)]
        if len(matching_commands) == 1:
            next_text = matching_commands[0][len(current_text):]
        else:
            common_prefix = os.path.commonprefix(matching_commands)
            next_text     = common_prefix[len(current_text):]

        pos_step = len(next_text)
        self.command = self.command + next_text
        self.current_command = self.command
        self.cursor_pos += pos_step
        if pos_step == 0 and len(matching_commands) > 0:
            propt_str = "\n> "
            for mc in matching_commands:
                propt_str += mc
                propt_str += " "
            propt_str += "\n"
            self.feedString(propt_str)
    
    def clearContent(self):
        self.buffer = ""
        self.lines  = [""]
        min_mid_canvas_height = self.modified_h
        self.canvas_size  = (self.size[0], min_mid_canvas_height)
        self.canvas_coord = (0,0)
        self.mid_canvas   = pygame.Surface( self.canvas_size,  pygame.SRCALPHA ) 
    
    def evaCommand(self):
        # 使用split函数以空格为分隔符拆分指令字符串
        parts = self.command.split()
        command = ""
        params  = []
        # 第一个部分是指令名
        if len(parts) > 0:
            command = parts[0]
        else:
            command = ""
        
        # 剩余部分是参数
        if len(parts) > 1:
            params = parts[1:]
        else:
            params = []
        
        if command == "clear":
            self.clearContent()
        elif command == "setTextColor":
            self.setTextColorCmd(params)
        elif command == "setBgColor":
            self.setBgColorCmd(params)
        elif command == "exportToFile":
            self.exportToFileCmd(params)
        elif command == "ip":
            self.ipShowCmd(params)

        else:
            self.feedString("\n> unknown command!\n")
            # asyncio.run(self.uniCommand())

    def onResize(self, new_size):
        nsx , nsy = new_size
        nsx = max(2.5*self.line_height, nsx)
        nsy = max(2.5*self.line_height, nsy)
        self.size = (nsx,nsy)
        self.modified_h      = self.size[1] - 1.3*self.line_height
        self.reGenerateLines()
        self.title_font_size = min(26, max(14, self.size[1] * 0.2 ))
        self.title_font      = gol.getFont(self.title_font_size)[0]

    def onMouseClick(self, mouse_x, mouse_y, btn):
        super().onMouseClick(mouse_x, mouse_y, btn)
        if self.OnModify == True:
            return 
        
        if self.passby:
            if btn == gol.MOUSEBUTTON_LEFT:
                self.fixing = not self.fixing
                if self.fixing:
                    self.cursor_time = 0

            if btn == gol.MOUSEBUTTON_WHEELDOWN:
                w, h    = self.size
                h -= self.line_height
                cw,ch   = self.canvas_size
                cx,cy   = self.canvas_coord
                ky      = 20
                new_cy  = min( cy + 2 * ky , ch - h)
                new_cy  = max( new_cy, 0 )
                self.canvas_coord = (cx, new_cy)
            if btn == gol.MOUSEBUTTON_WHEELUP:
                w, h    = self.size
                cw,ch   = self.canvas_size
                cx,cy   = self.canvas_coord
                ky      = -20
                new_cy  = min( cy + 2 * ky , ch - h)
                new_cy  = max( new_cy, 0 )
                self.canvas_coord = (cx, new_cy)

    
    def onKeyInput(self, key, unicode):
        if self.fixing == False:
            return 
        
        mods = pygame.key.get_mods()
        if key == pygame.K_BACKSPACE:
            if self.cursor_pos >= 1: 
                self.command = self.command[:self.cursor_pos-1] + self.command[self.cursor_pos:]
                self.current_command = self.command
                self.cursor_pos -= 1
        elif key == pygame.K_LEFT:  # 左方向键
            if self.cursor_pos > 0:
                self.cursor_time = 0
                self.cursor_pos -= 1
        elif key == pygame.K_RIGHT:  # 右方向键
            if self.cursor_pos < len(self.command):
                self.cursor_time = 0
                self.cursor_pos += 1
        elif key == pygame.K_UP:  # 上方向键
            if self.command_pos > 0:
                self.command_pos -= 1
                self.command = self.history_commands[self.command_pos]
                self.cursor_pos = len(self.command)

        elif key == pygame.K_DOWN: 
            if self.command_pos < len(self.history_commands) - 1 :
                self.command_pos += 1
                self.command = self.history_commands[self.command_pos]
                self.cursor_pos = len(self.command)
            elif self.command_pos == len(self.history_commands) - 1:
                self.command = self.current_command
                self.command_pos = len(self.history_commands) 
                self.cursor_pos = len(self.command)

        elif key == pygame.K_TAB:
            self.autoCompleter()

        elif key == pygame.K_c and mods & pygame.KMOD_CTRL:  # 检查 Ctrl+C
            self.command    = ""
            self.current_command = self.command
            self.cursor_pos = 0
        elif key == pygame.K_RETURN:
            self.evaCommand()
            self.history_commands.append(self.command)
            self.command_pos = len(self.history_commands)
            self.command     = ""
            self.current_command = self.command
            self.cursor_pos = 0
        elif unicode:
            self.command = self.command[:self.cursor_pos] + unicode + self.command[self.cursor_pos:]
            self.current_command = self.command
            self.cursor_pos += 1


class Canvas(Component):
    def __init__(self, coord, size, cid = -1) -> None:
        super().__init__(coord, size, cid)
        self.scale      = 1.0
        self.max_scale  = 4.8
        self.min_scale  = 0.04
        self.scale_v    = 0.0
        self.offset     = (0.5*size[0], 0.5*size[1])
        self.target_pos = (0,0)
        self.moving     = False

        self.nodes_bidi = None
        self.edges_bidi = None
        self.nodes      = [] 
        self.edges      = []
        self.ORI_G      = None # 总图
        self.G          = None # 显示的图
        self.GC         = None # 自定义功能包依赖图
        self.GH         = None # 引用图
        self.GH_ALL     = None # 引用图（含系统包）
        self.filter_only_cp = False
        self.first_scan = False
        self.layer_layout = True
        self.font, _    = gol.getFont(24)


        self.path_search_begin_node  = None
        self.path_search_target_node = None
        self.path_search_selecting_node = 0
        self.recent_path = []

        self.monitor       = getComponentByCid(22)
        self.scale_slider  = getComponentByCid(11)
        self.show_label    = getComponentByCid(6)
        self.show_label.color = get_contrast_color( gol.COMPONENT_WINDOW_COLOR1 )
        getComponentByCid(4).on = True
        self.scale_slider.min_value = self.min_scale
        self.scale_slider.max_value = self.max_scale

        self.custom_packages = []
        self.inc_content = {}
        self.package_include_directories = {}
        self.package_depend_content = {}
        self.package_cmakelist_path = {}

        self.last_selected_nodes = []
        self.last_selected_edges = []

        self.mouse_pos  = (0,0)
    
    def setShow(self, show_type):
        if self.first_scan == False:
            gol.state_bar.flash( "Scan first", "error" )
            return

        if show_type == 1: #custom packages
            if self.GC == None:
                self.GC = self.G.subgraph(self.custom_packages).copy()
            self.setG(self.GC, self.custom_packages, True)
            self.show_label.content = "Show: Custom"

        if show_type == 2: #all packages
            self.setG(self.ORI_G, self.custom_packages, True)
            self.show_label.content = "Show: All"

        if show_type == 3: #include graph
            if self.GH == None:
                self.calcGH()
            self.setG(self.GH_ALL, self.custom_packages, True) # 如果只想显示自定义包的话，就改成self.GH
            self.checkGH()
            self.show_label.content = "Show: Inclusion Graph"
    
    def calcGH(self):
        if self.first_scan == False:
            return
        if self.GH != None:
            return

        self.GH     = nx.DiGraph()
        self.GH_ALL = nx.DiGraph()
        packages_not_include_catkin_dir = []
        self.GH.add_nodes_from(self.custom_packages)
        self.GH_ALL.add_nodes_from(self.ORI_G.nodes)
        for node in self.custom_packages:
            predecessors = list(self.ORI_G.predecessors(node))
            if "${catkin_INCLUDE_DIRS}" in self.package_include_directories[node]:
                predecessors_edges = [(pkg, node) for pkg in predecessors]
                self.GH_ALL.add_edges_from(predecessors_edges)
                predecessors_edges_only_cus = [(pkg, node) for pkg in predecessors if pkg in self.custom_packages]
                self.GH.add_edges_from(predecessors_edges_only_cus)
            else:
                packages_not_include_catkin_dir.append(node)
        
        for node in packages_not_include_catkin_dir:
            depends_pkgs = self.package_depend_content[node]
            for depend_pkg in depends_pkgs:
                predecessors_only_cus = list(self.GH.predecessors(depend_pkg))
                predecessors_edges_only_cus = [(pkg, node) for pkg in predecessors_only_cus] # 在GH内不包含系统包
                self.GH.add_edges_from(predecessors_edges_only_cus)

                predecessors = list(self.GH_ALL.predecessors(depend_pkg))
                predecessors_edges = [(pkg, node) for pkg in predecessors] # 在GH内不包含系统包
                self.GH_ALL.add_edges_from(predecessors_edges)
    
    def checkGH(self):
        if self.GH == None:
            return
        
        error_nodes = []
        for node in self.custom_packages:
            lacked_p = []
            predecessors = list(self.ORI_G.predecessors(node))
            for pnode in predecessors:
                path_ret = self.pathCheckInGH(pnode, node)
                if path_ret == False:
                    lacked_p.append(str(pnode))
                    self.nodes_bidi[node].setError(True)
            if len(lacked_p) > 0:
                error_nodes.append((str(node), lacked_p))
        
        if len(error_nodes) > 0:
            output_str = "\n> check include_directories:\n"
            for enode in error_nodes:
                en,lp = enode
                output_str += ("package " + en + " depends on\n")
                for p in lp:
                    output_str += (p + "\n")
                output_str += "but not include them.\n"
            output_str += "\nTry to open responding CMakeLists.txt and add \'${catkin_INCLUDE_DIRS}\' to include_directories(...) \n"
            self.monitor.feedString(output_str)
        else:
            self.monitor.feedString("\n > include_directories: \nno problem.\n")
        

    def setIncludeContent(self, inc_content):
        self.inc_content = inc_content
    
    def setIncludeDirectories(self, package_include_directories):
        self.package_include_directories = package_include_directories

    def setIncludeDependContent(self, package_depend_content):
        self.package_depend_content = package_depend_content
    
    def setCmakeListPathes(self, package_cmakelist_path):
        self.package_cmakelist_path = package_cmakelist_path
    
    def setLayerLayout(self, state):
        self.layer_layout = state
        if self.first_scan == False:
            return
        self.setG(self.G, self.custom_packages, True)
    
    def labelWidth(self, label_name):
        text_obj  = self.font.render(label_name, True, (0,0,0,0))
        text_rect = text_obj.get_rect()
        text_w    = text_rect.width
        # return self.screenSizeTOWorld(1.8*text_w) 
        return 1.8*text_w
    
    def concentric_layout(self, G, y_gap=50):
        def generate_e(D):
            sorted_values = sorted(list(set(D.values())), reverse=True)
            E = {value: idx for idx, value in enumerate(sorted_values)}
            return E

        def index_posx(i, index, w , lx, rx):
            if index == 0:
                return random.uniform(-100,100), 0
            if index % 2 == 1:
                return rx + w/2 , 1
            return lx - w/2 , -1

        degree_diff = {node: G.in_degree(node) - G.out_degree(node) for node in G.nodes()}
        E = generate_e(degree_diff)

        cur_y = 0
        pos = {}
        for i, diff_val in enumerate(E):
            left_x  = 0
            right_x = 0
            nodes_with_diff = [node for node, diff in degree_diff.items() if diff == diff_val]
            for j, node in enumerate(nodes_with_diff):
                w   = self.labelWidth(str(node))
                pos_node_x, dir = index_posx(i, j, w, left_x, right_x)
                pos_node_y = y_gap * i
                cur_y = pos_node_y
                pos[node] = [pos_node_x, pos_node_y]

                if dir == -1:
                    left_x = pos_node_x - w/2
                if dir == 0:
                    left_x  = pos_node_x - w/2
                    right_x = pos_node_x + w/2
                if dir == 1:
                    right_x = pos_node_x + w/2
                
        return pos,cur_y


    def setG(self, G , custom_packages , do_not_modify_ori_G = False):
        self.nodes_bidi = None
        self.edges_bidi = None
        self.nodes      = [] 
        self.edges      = []
        self.G = G
        if do_not_modify_ori_G == False:  # new scan
            self.ORI_G = G
            self.GC    = None
            self.GH    = None
        self.custom_packages = custom_packages
        self.first_scan = True

        components = list(nx.weakly_connected_components(G))
        pos = {}
        total_y = 0
        for i, component in enumerate(components):
            subgraph = G.subgraph(component)
            # pos_subgraph = nx.spring_layout(subgraph, scale=1.5, iterations = 400, k = 2)
            # pos_subgraph = adjust_positions(pos_subgraph)

            if self.layer_layout == True:
                pos_subgraph, group_y = self.concentric_layout(subgraph, y_gap=40)
                dy = total_y
                total_y += (group_y + 40)
                # 添加偏移
                for node in pos_subgraph:
                    pos_subgraph[node][1] += dy
                pos.update(pos_subgraph)

            else:
                pos_subgraph = nx.spring_layout(subgraph, scale=3.5, iterations = 400, k = 2)
                pos_subgraph = adjust_positions(pos_subgraph)

                dx,dy = spiral_position(i)
                dx *= 4
                dy *= 4
                # 添加偏移
                for node in pos_subgraph:
                    pos_subgraph[node][0] += dx
                    pos_subgraph[node][1] += dy
                pos.update(pos_subgraph)


        cx,cy, num = 0,0,0
        node_dict = {}
        edge_dict = {}
        for node in G.nodes:
            x,y = pos[node]
            if self.layer_layout == False:
                x *= 100
                y *= 100
            is_cus = False
            if node in custom_packages:
                is_cus = True
            node_label = self.appendNode((x,y), str(node), is_cus)
            cx += x
            cy += y
            num += 1
            node_dict[node] = node_label
    
        for edge in G.edges:
            x,y = pos[edge[1]]
            if self.layer_layout == False:
                x *= 100
                y *= 100
            begin = (x,y)
            x,y = pos[edge[0]]
            if self.layer_layout == False:
                x *= 100
                y *= 100
            end = (x,y)
            edge_element = self.appendEdge(begin,end)
            edge_dict[edge] = edge_element
        
        self.nodes_bidi = bidict(node_dict)
        self.edges_bidi = bidict(edge_dict)

        if(num > 0):
            cx /= num
            cy /= num
            w,h        = self.size
            wdx, wdy   = self.screenSizeTOWorld(w/2), self.screenSizeTOWorld(h/2)
            self.offset = (-cx + wdx , -cy + wdy  )

        self.checkCircle()
    
    def checkCircle(self):
        # 找出所有的循环依赖
        cycles = list(nx.simple_cycles(self.G))
        for cycle in cycles:
            for node in cycle:
                node_element = self.nodes_bidi[node]
                node_element.setError(True)
            cycle.append(cycle[0])
            cycle_edges = [(cycle[i], cycle[i+1]) for i in range(len(cycle)-1)]
            for edge in cycle_edges:
                edge_element = self.edges_bidi[edge]
                edge_element.setError(True)

    
    def appendNode(self, pos, name, is_cus = False):
        node_label = CanvasLabel(pos,name, is_cus)
        self.nodes.append( node_label )
        return node_label
    
    def appendEdge(self, begin, end):
        edge_element = CanvasEdge(begin,end)
        self.edges.append( edge_element )
        return edge_element
    
    def worldCoordTOScreen(self, world_coord):
        wx,wy = world_coord
        ox,oy = self.offset
        sx    = (wx + ox) / self.scale
        sy    = (wy + oy) / self.scale
        return (sx,sy)
    
    def screenCoordTOWorld(self, screen_coord):
        sx,sy = screen_coord
        ox,oy = self.offset
        wx    = sx * self.scale - ox
        wy    = sy * self.scale - oy
        return (wx,wy)

    def worldSizeTOScreen(self, world_size):
        return world_size / self.scale
    
    def screenSizeTOWorld(self, screen_size):
        return screen_size * self.scale

    def setScale(self, value):
        mid_x,mid_y = self.size
        mid_x *= 0.5
        mid_y *= 0.5
        wx_old,wy_old = self.screenCoordTOWorld( (mid_x, mid_y) )
        self.scale = value
        wx,wy = self.screenCoordTOWorld( (mid_x, mid_y)  )
        ox,oy = self.offset
        self.offset = (ox + wx - wx_old, oy + wy - wy_old)

    def preRender(self):
        super().preRender()
        r,g,b,a = gol.LIST_BUTTON_BG_COLOR
        self.canvas.fill((r,g,b,255))
        self.scale_v *= 0.75
        if abs(self.scale_v) < 0.05:
            self.scale_v = 0


        wx_old,wy_old = self.screenCoordTOWorld( self.mouse_pos )
        self.scale += self.scale_v * 0.1
        self.scale  = min(self.max_scale , max(self.scale, self.min_scale))
        self.scale_slider.current_value = self.scale

        if abs(self.scale_v) > 0.05:
            wx,wy = self.screenCoordTOWorld( self.mouse_pos )
            ox,oy = self.offset
            self.offset = (ox + wx - wx_old, oy + wy - wy_old)

    def postRender(self, surface):
        for edge in self.edges:
            edge.render(self.canvas, self.size, self.worldCoordTOScreen, self.worldSizeTOScreen)
        for node in self.nodes:
            node.render(self.canvas, self.size, self.worldCoordTOScreen, self.worldSizeTOScreen)
        
        if self.path_search_selecting_node != 0:
            sx,sy    = self.worldCoordTOScreen( self.path_search_begin_node.world_coord )
            mx,my    = self.mouse_pos
            if self.path_search_selecting_node == 2:
                mx,my    = self.worldCoordTOScreen( self.path_search_target_node.world_coord )
            renderDottedLine(self.canvas, gol.COLOR_GREEN, (sx,sy), (mx,my), 8, 15 )

            path_len = len(self.recent_path)
            for i in range(path_len - 1):
                p1 = self.nodes_bidi[self.recent_path[i]].world_coord
                p2 = self.nodes_bidi[self.recent_path[i+1]].world_coord
                temp_edge = CanvasEdge(p2,p1, gol.COLOR_GREEN)
                temp_edge.render(self.canvas, self.size, self.worldCoordTOScreen, self.worldSizeTOScreen)


        super().postRender(surface)
    
    def onMouseMotion(self, mouse_x, mouse_y):
        x,y = self.coord
        w, h = self.size
        if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
            self.passby = True
        else:
            self.passby = False
        self.mouse_pos = ( mouse_x - x, mouse_y - y)
        if input_manager.isButtonDown(gol.MOUSEBUTTON_LEFT) and self.passby == True:
            dx = input_manager.mouse_x_vel
            dy = input_manager.mouse_y_vel
            ox,oy = self.offset
            self.offset = ( ox + dx*self.scale , oy+dy*self.scale )
    
    def onMouseClick(self, mouse_x, mouse_y, btn):
        if self.passby == False:
            return
        
        if btn == gol.MOUSEBUTTON_WHEELDOWN:
            self.scale_v = min(10, self.scale_v + 0.2)
        if btn == gol.MOUSEBUTTON_WHEELUP:
            self.scale_v = max(-10, self.scale_v - 0.2)
        
        if btn == gol.MOUSEBUTTON_LEFT:
            for node in self.nodes:
                if node.passby:
                    self.monitor.clearContent()
                    content = "Package " + node.name + " includes files: \n\n"
                    content += self.inc_content.get(node.name,"")
                    self.monitor.feedString(content)

        if btn == gol.MOUSEBUTTON_MID:
            for node in self.nodes:
                if node.passby:
                    gnode = self.nodes_bidi.inverse[node]
                    if gnode in self.custom_packages:
                        cmakelist_path = self.package_cmakelist_path[gnode]
                        try:
                            # 打开指定文件或目录在VSCode中
                            subprocess.run(["code", cmakelist_path])
                        except:
                            try:
                                # 如果VSCode打不开，则尝试用gedit打开
                                subprocess.run(["gedit", cmakelist_path])
                            except Exception as e:
                                self.monitor.feedString(f"> An error occurred while trying to open with gedit: {e}")
        
        click_ground = True
        if btn == gol.MOUSEBUTTON_RIGHT:
            for node in self.nodes:
                if node.passby:
                    click_ground = False
                    if self.path_search_begin_node == None:
                        self.path_search_begin_node = node
                        self.path_search_selecting_node = 1
                        break
                    elif self.path_search_target_node == None:
                        self.path_search_target_node = node
                        self.path_search_selecting_node = 2
                        self.pathSearch()
                        break
                    else:
                        self.path_search_begin_node  = node
                        self.path_search_target_node = None
                        self.path_search_selecting_node = 1
                        self.recent_path = []
                        break
            if click_ground == True:
                self.path_search_begin_node  = None
                self.path_search_target_node = None
                self.path_search_selecting_node = 0
                self.recent_path = []

    def pathCheckInGH(self, source_node, target_node):
        if self.GH_ALL == None:
            return False
        try:
            nx.shortest_path(self.GH_ALL, source=source_node, target=target_node)
            return True
        except nx.NetworkXNoPath:
            return False

    def pathSearch(self):
        if self.path_search_begin_node == None or self.path_search_target_node == None:
            self.monitor.feedString("Path search Error!\n")
            return
        source_node = self.nodes_bidi.inverse[self.path_search_begin_node]
        target_node = self.nodes_bidi.inverse[self.path_search_target_node]
        try:
            path = nx.shortest_path(self.G, source=source_node, target=target_node)
            self.monitor.feedString("Path found!\n")
            self.recent_path = path
        except nx.NetworkXNoPath:
            self.monitor.feedString("No Path found!\n")
    
    def update(self):

        for c in self.last_selected_edges:
            c.setCond(0)
        for c in self.last_selected_nodes:
            c.setCond(0)

        selected_nodes      = []
        for node in self.nodes:
            if node.checkMouseOn(self.mouse_pos, self.worldCoordTOScreen, self.worldSizeTOScreen):
                selected_nodes.append(node)
        
        self.last_selected_nodes = []
        self.last_selected_edges = []
        for snode in selected_nodes:
            gnode = self.nodes_bidi.inverse[snode]
            # 找到该节点的上游邻居和下游邻居
            predecessors = list(self.G.predecessors(gnode))
            successors   = list(self.G.successors(gnode))

            # 找到与该节点相关的边
            in_edges  = list(self.G.in_edges(gnode))
            out_edges = list(self.G.out_edges(gnode))

            for pn in predecessors:
                c = self.nodes_bidi[pn]
                c.setCond(1)
                self.last_selected_nodes.append(c)
            for sn in successors:
                c = self.nodes_bidi[sn]
                c.setCond(-1)
                self.last_selected_nodes.append(c)
            for ie in in_edges:
                c = self.edges_bidi[ie]
                c.setCond(1)
                self.last_selected_edges.append(c)
            for oe in out_edges:
                c = self.edges_bidi[oe]
                c.setCond(-1)
                self.last_selected_edges.append(c)
        






    
def getComponentByName(name):
    for component in gol.components:
        if isinstance(component, MiniTerminal):
            if component.title == name:
                return component
        elif isinstance(component, Button):
            if component.title == name:
                return component
        elif isinstance(component, ListButton):
            if component.title == name:
                return component
        elif isinstance(component, Slider):
            if component.title == name:
                return component
        elif isinstance(component, Label):
            if component.content == name:
                return component
    return None

def getComponentByCid(cid):
    for component in gol.components:
        if component.cid == cid:
            return component
    return None