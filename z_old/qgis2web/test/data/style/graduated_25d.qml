<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.18.7" simplifyAlgorithm="0" minimumScale="0" maximumScale="1e+08" simplifyDrawingHints="1" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" readOnly="0" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="cat">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="NAMES">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="AREA_MI">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="xlabel">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="ylabel">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="rotation">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
  </edittypes>
  <renderer-v2 attr="AREA_MI" forceraster="0" symbollevels="0" type="graduatedSymbol" graduatedMethod="GraduatedColor" enableorderby="1">
    <ranges>
      <range render="true" symbol="0" lower="20.056999999999999" upper="219.690599999999989" label=" 20.0570 - 219.6906 "/>
      <range render="true" symbol="1" lower="219.690599999999989" upper="419.324200000000019" label=" 219.6906 - 419.3242 "/>
      <range render="true" symbol="2" lower="419.324200000000019" upper="618.957800000000020" label=" 419.3242 - 618.9578 "/>
      <range render="true" symbol="3" lower="618.957800000000020" upper="818.591400000000021" label=" 618.9578 - 818.5914 "/>
      <range render="true" symbol="4" lower="818.591400000000021" upper="1018.225000000000023" label=" 818.5914 - 1018.2250 "/>
    </ranges>
    <symbols>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="0">
        <layer pass="0" class="SimpleFill" locked="1">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <effect enabled="1" type="effectStack">
            <effect type="outerGlow">
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="5"/>
              <prop k="color1" v="0,0,255,255"/>
              <prop k="color2" v="0,255,0,255"/>
              <prop k="color_type" v="0"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="single_color" v="17,17,17,255"/>
              <prop k="spread" v="4"/>
              <prop k="spread_unit" v="MapUnit"/>
              <prop k="spread_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="transparency" v="0.5"/>
            </effect>
          </effect>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="order_parts(   extrude(    segments_to_lines( $geometry ),    cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),    sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height )  ),  'distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))',  False)"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@0@1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="247,251,255,255"/>
              <prop k="color_dd_active" v="1"/>
              <prop k="color_dd_expression" v="set_color_part(   @symbol_color, 'value',  40 + 19 * abs( $pi - azimuth(     point_n( geometry_n($geometry, @geometry_part_num) , 1 ),     point_n( geometry_n($geometry, @geometry_part_num) , 2 )  ) ) )"/>
              <prop k="color_dd_field" v=""/>
              <prop k="color_dd_useexpr" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="119,119,119,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="translate(  $geometry,  cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),  sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ))"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@0@2">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="247,251,255,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="177,169,124,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="1">
        <layer pass="0" class="SimpleFill" locked="1">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <effect enabled="1" type="effectStack">
            <effect type="outerGlow">
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="5"/>
              <prop k="color1" v="0,0,255,255"/>
              <prop k="color2" v="0,255,0,255"/>
              <prop k="color_type" v="0"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="single_color" v="17,17,17,255"/>
              <prop k="spread" v="4"/>
              <prop k="spread_unit" v="MapUnit"/>
              <prop k="spread_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="transparency" v="0.5"/>
            </effect>
          </effect>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="order_parts(   extrude(    segments_to_lines( $geometry ),    cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),    sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height )  ),  'distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))',  False)"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@1@1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="200,221,240,255"/>
              <prop k="color_dd_active" v="1"/>
              <prop k="color_dd_expression" v="set_color_part(   @symbol_color, 'value',  40 + 19 * abs( $pi - azimuth(     point_n( geometry_n($geometry, @geometry_part_num) , 1 ),     point_n( geometry_n($geometry, @geometry_part_num) , 2 )  ) ) )"/>
              <prop k="color_dd_field" v=""/>
              <prop k="color_dd_useexpr" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="119,119,119,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="translate(  $geometry,  cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),  sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ))"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@1@2">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="200,221,240,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="177,169,124,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="2">
        <layer pass="0" class="SimpleFill" locked="1">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <effect enabled="1" type="effectStack">
            <effect type="outerGlow">
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="5"/>
              <prop k="color1" v="0,0,255,255"/>
              <prop k="color2" v="0,255,0,255"/>
              <prop k="color_type" v="0"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="single_color" v="17,17,17,255"/>
              <prop k="spread" v="4"/>
              <prop k="spread_unit" v="MapUnit"/>
              <prop k="spread_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="transparency" v="0.5"/>
            </effect>
          </effect>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="order_parts(   extrude(    segments_to_lines( $geometry ),    cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),    sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height )  ),  'distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))',  False)"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@2@1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="115,179,216,255"/>
              <prop k="color_dd_active" v="1"/>
              <prop k="color_dd_expression" v="set_color_part(   @symbol_color, 'value',  40 + 19 * abs( $pi - azimuth(     point_n( geometry_n($geometry, @geometry_part_num) , 1 ),     point_n( geometry_n($geometry, @geometry_part_num) , 2 )  ) ) )"/>
              <prop k="color_dd_field" v=""/>
              <prop k="color_dd_useexpr" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="119,119,119,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="translate(  $geometry,  cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),  sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ))"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@2@2">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="115,179,216,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="177,169,124,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="3">
        <layer pass="0" class="SimpleFill" locked="1">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <effect enabled="1" type="effectStack">
            <effect type="outerGlow">
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="5"/>
              <prop k="color1" v="0,0,255,255"/>
              <prop k="color2" v="0,255,0,255"/>
              <prop k="color_type" v="0"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="single_color" v="17,17,17,255"/>
              <prop k="spread" v="4"/>
              <prop k="spread_unit" v="MapUnit"/>
              <prop k="spread_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="transparency" v="0.5"/>
            </effect>
          </effect>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="order_parts(   extrude(    segments_to_lines( $geometry ),    cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),    sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height )  ),  'distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))',  False)"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@3@1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="40,121,185,255"/>
              <prop k="color_dd_active" v="1"/>
              <prop k="color_dd_expression" v="set_color_part(   @symbol_color, 'value',  40 + 19 * abs( $pi - azimuth(     point_n( geometry_n($geometry, @geometry_part_num) , 1 ),     point_n( geometry_n($geometry, @geometry_part_num) , 2 )  ) ) )"/>
              <prop k="color_dd_field" v=""/>
              <prop k="color_dd_useexpr" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="119,119,119,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="translate(  $geometry,  cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),  sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ))"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@3@2">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="40,121,185,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="177,169,124,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="4">
        <layer pass="0" class="SimpleFill" locked="1">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <effect enabled="1" type="effectStack">
            <effect type="outerGlow">
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="5"/>
              <prop k="color1" v="0,0,255,255"/>
              <prop k="color2" v="0,255,0,255"/>
              <prop k="color_type" v="0"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="single_color" v="17,17,17,255"/>
              <prop k="spread" v="4"/>
              <prop k="spread_unit" v="MapUnit"/>
              <prop k="spread_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="transparency" v="0.5"/>
            </effect>
          </effect>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="order_parts(   extrude(    segments_to_lines( $geometry ),    cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),    sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height )  ),  'distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))',  False)"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@4@1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="8,48,107,255"/>
              <prop k="color_dd_active" v="1"/>
              <prop k="color_dd_expression" v="set_color_part(   @symbol_color, 'value',  40 + 19 * abs( $pi - azimuth(     point_n( geometry_n($geometry, @geometry_part_num) , 1 ),     point_n( geometry_n($geometry, @geometry_part_num) , 2 )  ) ) )"/>
              <prop k="color_dd_field" v=""/>
              <prop k="color_dd_useexpr" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="119,119,119,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="translate(  $geometry,  cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),  sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ))"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@4@2">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="8,48,107,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="177,169,124,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="0">
        <layer pass="0" class="SimpleFill" locked="1">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,255,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <effect enabled="1" type="effectStack">
            <effect type="outerGlow">
              <prop k="blend_mode" v="0"/>
              <prop k="blur_level" v="5"/>
              <prop k="color1" v="0,0,255,255"/>
              <prop k="color2" v="0,255,0,255"/>
              <prop k="color_type" v="0"/>
              <prop k="discrete" v="0"/>
              <prop k="draw_mode" v="2"/>
              <prop k="enabled" v="1"/>
              <prop k="single_color" v="17,17,17,255"/>
              <prop k="spread" v="4"/>
              <prop k="spread_unit" v="MapUnit"/>
              <prop k="spread_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="transparency" v="0.5"/>
            </effect>
          </effect>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="order_parts(   extrude(    segments_to_lines( $geometry ),    cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),    sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height )  ),  'distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))',  False)"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@0@1">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="153,228,125,255"/>
              <prop k="color_dd_active" v="1"/>
              <prop k="color_dd_expression" v="set_color_part(   @symbol_color, 'value',  40 + 19 * abs( $pi - azimuth(     point_n( geometry_n($geometry, @geometry_part_num) , 1 ),     point_n( geometry_n($geometry, @geometry_part_num) , 2 )  ) ) )"/>
              <prop k="color_dd_field" v=""/>
              <prop k="color_dd_useexpr" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="119,119,119,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
        <layer pass="0" class="GeometryGenerator" locked="0">
          <prop k="SymbolType" v="Fill"/>
          <prop k="geometryModifier" v="translate(  $geometry,  cos( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ),  sin( radians( eval( @qgis_25d_angle ) ) ) * eval( @qgis_25d_height ))"/>
          <symbol alpha="1" clip_to_extent="1" type="fill" name="@0@2">
            <layer pass="0" class="SimpleFill" locked="0">
              <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="color" v="153,228,125,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="177,169,124,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0.26"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
            </layer>
          </symbol>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <prop k="color1" v="247,251,255,255"/>
      <prop k="color2" v="8,48,107,255"/>
      <prop k="discrete" v="0"/>
      <prop k="stops" v="0.13;222,235,247,255:0.26;198,219,239,255:0.39;158,202,225,255:0.52;107,174,214,255:0.65;66,146,198,255:0.78;33,113,181,255:0.9;8,81,156,255"/>
    </colorramp>
    <invertedcolorramp value="0"/>
    <mode name="equal"/>
    <rotation/>
    <sizescale scalemethod="diameter"/>
    <labelformat format=" %1 - %2 " trimtrailingzeroes="false" decimalplaces="0"/>
    <orderby>
      <orderByClause asc="0" nullsFirst="1">distance(  $geometry,  translate(    @map_extent_center,    1000 * @map_extent_width * cos( radians( @qgis_25d_angle + 180 ) ),    1000 * @map_extent_width * sin( radians( @qgis_25d_angle + 180 ) )  ))</orderByClause>
    </orderby>
  </renderer-v2>
  <labeling type="simple"/>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="labeling" value="pal"/>
    <property key="labeling/addDirectionSymbol" value="false"/>
    <property key="labeling/angleOffset" value="0"/>
    <property key="labeling/blendMode" value="0"/>
    <property key="labeling/bufferBlendMode" value="0"/>
    <property key="labeling/bufferColorA" value="255"/>
    <property key="labeling/bufferColorB" value="255"/>
    <property key="labeling/bufferColorG" value="255"/>
    <property key="labeling/bufferColorR" value="255"/>
    <property key="labeling/bufferDraw" value="false"/>
    <property key="labeling/bufferJoinStyle" value="64"/>
    <property key="labeling/bufferNoFill" value="false"/>
    <property key="labeling/bufferSize" value="1"/>
    <property key="labeling/bufferSizeInMapUnits" value="false"/>
    <property key="labeling/bufferSizeMapUnitMaxScale" value="0"/>
    <property key="labeling/bufferSizeMapUnitMinScale" value="0"/>
    <property key="labeling/bufferSizeMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/bufferTransp" value="0"/>
    <property key="labeling/centroidInside" value="false"/>
    <property key="labeling/centroidWhole" value="false"/>
    <property key="labeling/decimals" value="3"/>
    <property key="labeling/displayAll" value="false"/>
    <property key="labeling/dist" value="0"/>
    <property key="labeling/distInMapUnits" value="false"/>
    <property key="labeling/distMapUnitMaxScale" value="0"/>
    <property key="labeling/distMapUnitMinScale" value="0"/>
    <property key="labeling/distMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/drawLabels" value="false"/>
    <property key="labeling/enabled" value="false"/>
    <property key="labeling/fieldName" value=""/>
    <property key="labeling/fitInPolygonOnly" value="false"/>
    <property key="labeling/fontBold" value="false"/>
    <property key="labeling/fontCapitals" value="0"/>
    <property key="labeling/fontFamily" value="MS Shell Dlg 2"/>
    <property key="labeling/fontItalic" value="false"/>
    <property key="labeling/fontLetterSpacing" value="0"/>
    <property key="labeling/fontLimitPixelSize" value="false"/>
    <property key="labeling/fontMaxPixelSize" value="10000"/>
    <property key="labeling/fontMinPixelSize" value="3"/>
    <property key="labeling/fontSize" value="8.25"/>
    <property key="labeling/fontSizeInMapUnits" value="false"/>
    <property key="labeling/fontSizeMapUnitMaxScale" value="0"/>
    <property key="labeling/fontSizeMapUnitMinScale" value="0"/>
    <property key="labeling/fontSizeMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/fontStrikeout" value="false"/>
    <property key="labeling/fontUnderline" value="false"/>
    <property key="labeling/fontWeight" value="50"/>
    <property key="labeling/fontWordSpacing" value="0"/>
    <property key="labeling/formatNumbers" value="false"/>
    <property key="labeling/isExpression" value="true"/>
    <property key="labeling/labelOffsetInMapUnits" value="true"/>
    <property key="labeling/labelOffsetMapUnitMaxScale" value="0"/>
    <property key="labeling/labelOffsetMapUnitMinScale" value="0"/>
    <property key="labeling/labelOffsetMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/labelPerPart" value="false"/>
    <property key="labeling/leftDirectionSymbol" value="&lt;"/>
    <property key="labeling/limitNumLabels" value="false"/>
    <property key="labeling/maxCurvedCharAngleIn" value="20"/>
    <property key="labeling/maxCurvedCharAngleOut" value="-20"/>
    <property key="labeling/maxNumLabels" value="2000"/>
    <property key="labeling/mergeLines" value="false"/>
    <property key="labeling/minFeatureSize" value="0"/>
    <property key="labeling/multilineAlign" value="0"/>
    <property key="labeling/multilineHeight" value="1"/>
    <property key="labeling/namedStyle" value="Normal"/>
    <property key="labeling/obstacle" value="true"/>
    <property key="labeling/obstacleFactor" value="1"/>
    <property key="labeling/obstacleType" value="0"/>
    <property key="labeling/offsetType" value="0"/>
    <property key="labeling/placeDirectionSymbol" value="0"/>
    <property key="labeling/placement" value="1"/>
    <property key="labeling/placementFlags" value="0"/>
    <property key="labeling/plussign" value="false"/>
    <property key="labeling/predefinedPositionOrder" value="TR,TL,BR,BL,R,L,TSR,BSR"/>
    <property key="labeling/preserveRotation" value="true"/>
    <property key="labeling/previewBkgrdColor" value="#ffffff"/>
    <property key="labeling/priority" value="5"/>
    <property key="labeling/quadOffset" value="4"/>
    <property key="labeling/repeatDistance" value="0"/>
    <property key="labeling/repeatDistanceMapUnitMaxScale" value="0"/>
    <property key="labeling/repeatDistanceMapUnitMinScale" value="0"/>
    <property key="labeling/repeatDistanceMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/repeatDistanceUnit" value="1"/>
    <property key="labeling/reverseDirectionSymbol" value="false"/>
    <property key="labeling/rightDirectionSymbol" value=">"/>
    <property key="labeling/scaleMax" value="10000000"/>
    <property key="labeling/scaleMin" value="1"/>
    <property key="labeling/scaleVisibility" value="false"/>
    <property key="labeling/shadowBlendMode" value="6"/>
    <property key="labeling/shadowColorB" value="0"/>
    <property key="labeling/shadowColorG" value="0"/>
    <property key="labeling/shadowColorR" value="0"/>
    <property key="labeling/shadowDraw" value="false"/>
    <property key="labeling/shadowOffsetAngle" value="135"/>
    <property key="labeling/shadowOffsetDist" value="1"/>
    <property key="labeling/shadowOffsetGlobal" value="true"/>
    <property key="labeling/shadowOffsetMapUnitMaxScale" value="0"/>
    <property key="labeling/shadowOffsetMapUnitMinScale" value="0"/>
    <property key="labeling/shadowOffsetMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shadowOffsetUnits" value="1"/>
    <property key="labeling/shadowRadius" value="1.5"/>
    <property key="labeling/shadowRadiusAlphaOnly" value="false"/>
    <property key="labeling/shadowRadiusMapUnitMaxScale" value="0"/>
    <property key="labeling/shadowRadiusMapUnitMinScale" value="0"/>
    <property key="labeling/shadowRadiusMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shadowRadiusUnits" value="1"/>
    <property key="labeling/shadowScale" value="100"/>
    <property key="labeling/shadowTransparency" value="30"/>
    <property key="labeling/shadowUnder" value="0"/>
    <property key="labeling/shapeBlendMode" value="0"/>
    <property key="labeling/shapeBorderColorA" value="255"/>
    <property key="labeling/shapeBorderColorB" value="128"/>
    <property key="labeling/shapeBorderColorG" value="128"/>
    <property key="labeling/shapeBorderColorR" value="128"/>
    <property key="labeling/shapeBorderWidth" value="0"/>
    <property key="labeling/shapeBorderWidthMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeBorderWidthMapUnitMinScale" value="0"/>
    <property key="labeling/shapeBorderWidthMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeBorderWidthUnits" value="1"/>
    <property key="labeling/shapeDraw" value="false"/>
    <property key="labeling/shapeFillColorA" value="255"/>
    <property key="labeling/shapeFillColorB" value="255"/>
    <property key="labeling/shapeFillColorG" value="255"/>
    <property key="labeling/shapeFillColorR" value="255"/>
    <property key="labeling/shapeJoinStyle" value="64"/>
    <property key="labeling/shapeOffsetMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeOffsetMapUnitMinScale" value="0"/>
    <property key="labeling/shapeOffsetMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeOffsetUnits" value="1"/>
    <property key="labeling/shapeOffsetX" value="0"/>
    <property key="labeling/shapeOffsetY" value="0"/>
    <property key="labeling/shapeRadiiMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeRadiiMapUnitMinScale" value="0"/>
    <property key="labeling/shapeRadiiMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeRadiiUnits" value="1"/>
    <property key="labeling/shapeRadiiX" value="0"/>
    <property key="labeling/shapeRadiiY" value="0"/>
    <property key="labeling/shapeRotation" value="0"/>
    <property key="labeling/shapeRotationType" value="0"/>
    <property key="labeling/shapeSVGFile" value=""/>
    <property key="labeling/shapeSizeMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeSizeMapUnitMinScale" value="0"/>
    <property key="labeling/shapeSizeMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeSizeType" value="0"/>
    <property key="labeling/shapeSizeUnits" value="1"/>
    <property key="labeling/shapeSizeX" value="0"/>
    <property key="labeling/shapeSizeY" value="0"/>
    <property key="labeling/shapeTransparency" value="0"/>
    <property key="labeling/shapeType" value="0"/>
    <property key="labeling/substitutions" value="&lt;substitutions/>"/>
    <property key="labeling/textColorA" value="255"/>
    <property key="labeling/textColorB" value="0"/>
    <property key="labeling/textColorG" value="0"/>
    <property key="labeling/textColorR" value="0"/>
    <property key="labeling/textTransp" value="0"/>
    <property key="labeling/upsidedownLabels" value="0"/>
    <property key="labeling/useSubstitutions" value="false"/>
    <property key="labeling/wrapChar" value=""/>
    <property key="labeling/xOffset" value="0"/>
    <property key="labeling/yOffset" value="0"/>
    <property key="labeling/zIndex" value="0"/>
    <property key="qgis2web/Visible" value="true"/>
    <property key="qgis2web/popup/AREA_MI" value="no label"/>
    <property key="qgis2web/popup/NAMES" value="no label"/>
    <property key="qgis2web/popup/cat" value="no label"/>
    <property key="qgis2web/popup/rotation" value="no label"/>
    <property key="qgis2web/popup/xlabel" value="no label"/>
    <property key="qgis2web/popup/ylabel" value="no label"/>
    <property key="variableNames">
      <value>qgis_25d_angle</value>
      <value>qgis_25d_height</value>
    </property>
    <property key="variableValues">
      <value>70</value>
      <value>10</value>
    </property>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerTransparency>0</layerTransparency>
  <displayfield>NAMES</displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Label"/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <SingleCategoryDiagramRenderer diagramType="Histogram" sizeLegend="0" attributeLegend="1">
    <DiagramCategory penColor="#000000" labelPlacementMethod="XHeight" penWidth="0" diagramOrientation="Up" sizeScale="0,0,0,0,0,0" minimumSize="0" barWidth="5" penAlpha="255" maxScaleDenominator="1e+08" backgroundColor="#ffffff" transparency="0" width="15" scaleDependency="Area" backgroundAlpha="255" angleOffset="1440" scaleBasedVisibility="0" enabled="0" height="15" lineSizeScale="0,0,0,0,0,0" sizeType="MM" lineSizeType="MM" minScaleDenominator="inf">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" color="#000000" label=""/>
    </DiagramCategory>
    <symbol alpha="1" clip_to_extent="1" type="marker" name="sizeSymbol">
      <layer pass="0" class="SimpleMarker" locked="0">
        <prop k="angle" v="0"/>
        <prop k="color" v="255,0,0,255"/>
        <prop k="horizontal_anchor_point" v="1"/>
        <prop k="joinstyle" v="bevel"/>
        <prop k="name" v="circle"/>
        <prop k="offset" v="0,0"/>
        <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
        <prop k="offset_unit" v="MM"/>
        <prop k="outline_color" v="0,0,0,255"/>
        <prop k="outline_style" v="solid"/>
        <prop k="outline_width" v="0"/>
        <prop k="outline_width_map_unit_scale" v="0,0,0,0,0,0"/>
        <prop k="outline_width_unit" v="MM"/>
        <prop k="scale_method" v="diameter"/>
        <prop k="size" v="2"/>
        <prop k="size_map_unit_scale" v="0,0,0,0,0,0"/>
        <prop k="size_unit" v="MM"/>
        <prop k="vertical_anchor_point" v="1"/>
      </layer>
    </symbol>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings yPosColumn="-1" showColumn="-1" linePlacementFlags="10" placement="0" dist="0" xPosColumn="-1" priority="0" obstacle="0" zIndex="0" showAll="1"/>
  <annotationform>.</annotationform>
  <aliases>
    <alias field="cat" index="0" name=""/>
    <alias field="NAMES" index="1" name=""/>
    <alias field="AREA_MI" index="2" name=""/>
    <alias field="xlabel" index="3" name=""/>
    <alias field="ylabel" index="4" name=""/>
    <alias field="rotation" index="5" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeactions default="-1"/>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column width="-1" hidden="0" type="field" name="cat"/>
      <column width="-1" hidden="0" type="field" name="NAMES"/>
      <column width="-1" hidden="0" type="field" name="AREA_MI"/>
      <column width="-1" hidden="0" type="field" name="xlabel"/>
      <column width="-1" hidden="0" type="field" name="ylabel"/>
      <column width="-1" hidden="0" type="field" name="rotation"/>
      <column width="-1" hidden="1" type="actions"/>
    </columns>
  </attributetableconfig>
  <editform>.</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>.</editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <widgets/>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <defaults>
    <default field="cat" expression=""/>
    <default field="NAMES" expression=""/>
    <default field="AREA_MI" expression=""/>
    <default field="xlabel" expression=""/>
    <default field="ylabel" expression=""/>
    <default field="rotation" expression=""/>
  </defaults>
  <previewExpression></previewExpression>
  <layerGeometryType>2</layerGeometryType>
</qgis>
