from .core import *
from .material import *
from .material.Material import Material
from .material import dispersion
from . import Field
from tabulate import tabulate
import types

class Waveguide:
	"""	 Waveguide class
	
	 General purpose waveguide class 
	
				  |<   w   >|
				 _________		  _____
				 |		 |			^
	  ___	_____|		 |_____ 
	   ^						    h
	   t								  
	  _v_	_____________________ __v__
	
	
	 PROPERTIES:
	
	 w - core width
	 h - core height
	 t - slab thickess for rib waveguides (def. 0)
	
	 To represent a slab (planar) waveguide, choose t = h."""
	__slots__ = [
				"_clad",
				"_core",
				"_subs",
				"_w",
				"_h",
				"_t"]
	def __init__(self,**kwargs):
		_in = kwargs.keys()
		slots = [i[1:] for i in self.__slots__]
		for i in _in:
			if i not in slots[:]:
				raise AttributeError(f"'Waveguide' object has no attribute '{i}'")
		if "clad" in _in:
			if type(kwargs["clad"]) in [types.FunctionType, float, int]:
				self._clad = Material(kwargs["clad"])
			elif (str(type(kwargs["clad"])) == "<class 'awg.material.Material.Material'>"):
				self._clad = kwargs["clad"]
			elif type(kwargs["clad"]) == list:
				self._clad = Material(list_to_array(kwargs["clad"]))
			elif str(type(kwargs["clad"])) == "<class 'numpy.ndarray'>":
				self._clad = Material(kwargs["clad"])
			else:
				raise ValueError("The cladding must be a material or a float representing its refractive index.")
		else:
			self._clad = Material(SiO2)

		if "core" in _in:
			if type(kwargs["core"]) in [types.FunctionType, float, int]:
				self._core = Material(kwargs["core"])
			elif (str(type(kwargs["core"])) == "<class 'awg.material.Material.Material'>"):
				self._core = kwargs["core"]
			elif type(kwargs["core"]) == list:
				self._core = Material(list_to_array(kwargs["core"]))
			elif str(type(kwargs["core"])) == "<class 'numpy.ndarray'>":
				self._core = Material(kwargs["core"])
			else:
				raise ValueError("The core must be a material or a float representing its refractive index.")
		else:
			self._core = Material(Si)

		if "subs" in _in:
			if type(kwargs["subs"]) in [types.FunctionType, float, int]:
				self._subs = Material(kwargs["subs"])
			elif (str(type(kwargs["subs"])) == "<class 'awg.material.Material.Material'>"):
				self._subs = kwargs["subs"]
			elif type(kwargs["subs"]) == list:
				self._subs = Material(list_to_array(kwargs["subs"]))
			elif str(type(kwargs["subs"])) == "<class 'numpy.ndarray'>":
				self._subs = Material(kwargs["subs"])
			else:
				raise ValueError("The substrate must be a material or a float representing its refractive index.")
		else:
			self._subs = Material(SiO2)

		if "w" in _in:
			if type(kwargs["w"]) in [int, float] and kwargs["w"] > 0:
				self._w = kwargs["w"]
			else: 
				raise ValueError("The array waveguide core width 'w' [um] must be positive and be a float or an integer.")
		else:
			self._w = 0.500

		if "h" in _in:
			if type(kwargs["h"]) in [int, float] and kwargs["h"] > 0:
				self._h = kwargs["h"]
			else: 
				raise ValueError("The array waveguide core height 'h' [um] must be positive and be a float or an integer.")
		else:
			self._h = 0.200

		if "t" in _in:
			if type(kwargs["t"]) in [int, float] and kwargs["t"] >= 0:
				self._t = kwargs["t"]
			else: 
				raise ValueError("The array waveguide slab thickness 't' (for rib waveguides) [um] must be non-negative and be a float or an integer.")
		else:
			self._t = 0

	def index(self,lmbda, modes = np.inf, T = 295):
		""" 
		Return the index at a specific wavelength.

		lmbda - wavelenght [μm]
		modes - Number of modes to consider
		T     - Température of the material [K] (optional)(def.295)
		"""
		n1 = self.core.index(lmbda)
		n2 = self.clad.index(lmbda)
		n3 = self.subs.index(lmbda)
		return wgindex(lmbda,self.w, self.h,self.t,n2,n1,n3, Modes =  modes)

	def dispersion(self, lmbda1,lmbda2, point = 100):
		"""
		Return the dispersion relation between 2 wavelenght.

		lmdba1 - minimal wavelenght to consider [μm]
		lmbda2 - maximal wavelenght to consider [μm]
		point  - number of point to consider in the relation (def.100)

		"""
		return dispersion.dispersion(self.index,lmbda1,lmbda2, point = point)


	def groupindex(self,lmbda,T = 295):
		"""
		Return the group index at a specific wavelenght.

		lmbda - Wavelenght to consider [μm]
		T     - Temperature of the material [K] (optional)(def.295)

		"""
		n0 = self.index(lmbda,T)
		n1 = self.index(lmbda-0.1,T)
		n2 = self.index(lmbda+0.1,T)

		return n0 -lmbda*(n2-n1)/2

	def groupDispersion(self,lmbda1,lmbda2, point = 100):
		"""
		Return the group dispersion relation between 2 wavelenght.

		lmdba1 - minimal wavelenght to consider [μm]
		lmbda2 - maximal wavelenght to consider [μm]
		point  - number of point to consider in the relation (def.100)

		"""

		return dispersion.dispersion(self.groupindex,lmbda1,lmbda2,point = point)

	def mode(self,lmbda,**kwargs):
		"""
		Generate the waveguide mode at a specific wavelenght.


		lmbda     - Wavelenght at wich the mode will be generated
		ModeTyepe - The type of mode to consider (optional) (def.gaussian)
						rect     - generate a rectangular mode
						gaussian - generate mode with the gaussian approximation
						solve    - generate mode with the effetive index methode
		XLimits   - range along the x to consider in the mode generation (optional)
		point     - number of point to consider in the mode generation (def.100)
		"""
		
		_in = kwargs.keys()

		x = kwargs["x"] if "x" in _in else []
		ModeType = kwargs["ModeType"] if "ModeType" in _in else "gaussian"
		if "XLimits" in _in:
			XLimits = kwargs["XLimits"]
		else:
			XLimits = [-3*self._w,3*self._w]

		points = kwargs["points"] if "points" in _in else 100
		n1 = self.core.index(lmbda)
		n2 = self.clad.index(lmbda)
		n3 = self.subs.index(lmbda)

		if len(x) == 0:
			x = np.linspace(XLimits[0],XLimits[1],points)

		if ModeType == "gaussian":
			E,H,_ = gmode(lmbda, self._w, self._h, n2, n1, x = x)

			return Field.Field(x,E,([],H))

		elif ModeType == "rect":
			n = (n1+n2)/2
			n0 = 120*np.pi
			E = 1/(self._w**(1/4))*rect(x/self._w)
			H = n/n0 * 1/(self._w**(1/4))*rect(x/self._w)

		elif ModeType == "solve":
			E,H, _, _ = wgmode(lmbda,self._w,self._h,self._t,n2,n1,n3,x = x)
			return Field.Field(x,E,H)
		else:
			raise ValueError("Unknow mode type")


	def __str__(self):
		if type(self._clad.model) == types.FunctionType:
			clad = self._clad.model.__name__
		elif self._clad.type == "constant":
			clad = self._clad.model
		elif self._clad.type == "polynomial":
			if len(self._clad.model) <= 3:
				clad = self._clad.model
			else:
				clad = f"[{self._clad.model[0]},...,{self._clad.model[-1]}]"
		elif self._clad.type == "lookup":
			clad = "lookup table"

		if type(self._core.model) == types.FunctionType:
			core = self._core.model.__name__
		elif self._core.type == "constant":
			core = self._core.model
		elif self._core.type == "polynomial":
			if len(self._core.model) <= 3:
				core = self._core.model
			else:
				core = f"[{self._core.model[0]},...,{self._core.model[-1]}]"
		elif self._core.type == "lookup":
			core = "lookup table"

		if type(self._subs.model) == types.FunctionType:
			subs = self._subs.model.__name__
		elif self._subs.type == "constant":
			subs = self._subs.model
		elif self._subs.type == "polynomial":
			if len(self._subs.model) <= 3:
				subs = self._subs.model
			else:
				subs = f"[{self._subs.model[0]},...,{self._subs.model[-1]}]"
		elif self._subs.type == "lookup":
			subs = "lookup table"

		return tabulate([['clad', clad , "clad material"], ['core', core, "core material"], 
					['subs', subs, "subs material"],['w', self._w,"core width [\u03BCm]"],['h', self._h,"core height [\u03BCm]"],
					["t",self._t,"slab thickess for rib waveguides [\u03BCm]"]], headers=['parameters', 'Value', 'definition'])



    ### Define getter and setter for the Waveguide object ### 
	@property
	def clad(self):
		return self._clad
	
	@clad.setter
	def clad(self,clad):
		if (type(clad) == types.FunctionType) or (str(type(clad)) == "<class 'material.Material.Material'>") or (type(clad) == float) or (type(clad) == int):
			self._clad = Material(clad)
		elif type(clad) == list:
			self._clad = Material(list_to_array(clad))
		else:
			raise ValueError("The cladding must be a material or a float representing its refractive index.")

	@property
	def core(self):
		return self._core
	
	@core.setter
	def core(self,core):
		if (type(core) == types.FunctionType) or (str(type(core)) == "<class 'material.Material.Material'>") or (type(core) == float) or (type(core) == int):
			self._core = Material(core)
		elif type(core) == list:
			self._core = Material(list_to_array(core))
		else:
			raise ValueError("The core must be a material or a float representing its refractive index.")

	@property
	def subs(self):
		return self._subs
	
	@subs.setter
	def subs(self,subs):
		if (type(subs) == types.FunctionType) or (str(type(subs)) == "<class 'material.Material.Material'>") or (type(subs) == float) or (type(subs) == int):
			self._subs = subs
		elif type(subs) == list:
				self._subs = Material(list_to_array(subs))
		else:
			raise ValueError("The substrate must be a material or a float representing its refractive index.")

	@property
	def w(self):
		return self._w

	@w.setter
	def w(self,w):
		if type(w) in [int, float] and w > 0:
			self._w = w
		else:
			raise ValueError("The array waveguide core width 'w' [um] must be positive and be a float or an integer.")

	@property
	def h(self):
		return self._h

	@h.setter
	def h(self,h):
		if type(h) in [int, float] and h > 0:
			self._h = h
		else:
			raise ValueError("The array waveguide core height 'h' [um] must be positive and be a float or an integer.")

	@property
	def t(self):
		return self._t

	@t.setter
	def t(self,t):
		if type(t) in [int, float] and t >= 0:
			self._t = t
		else:
			raise ValueError("The array waveguide slab thickness 't' (for rib waveguides) [um] must be non-negative and be a float or an integer.")
